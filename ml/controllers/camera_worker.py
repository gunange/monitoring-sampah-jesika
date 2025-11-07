import cv2, time
import threading
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from typing import Callable, Any

from ml.app.config import get_int, get_str
from ml.app.utils import ensure_dir, timestamp_str
from ml.app.camera_open import parse_camera_src, open_capture

@dataclass
class CameraContext:
    state_lock: threading.Lock
    camera_status: dict
    set_latest_jpeg: Callable[[bytes | None], None]
    set_latest_raw_jpeg: Callable[[bytes | None], None]  # jika diperlukan
    update_metrics: Callable[[dict], None]
    save_detections_getter: Callable[[], bool]
    knn_model_getter: Callable[[], Any]
    logger: Any

def camera_worker(stop_event: threading.Event, ctx: CameraContext):
    src = parse_camera_src()
    backend = get_str("CAMERA_BACKEND", "AVFOUNDATION")
    interval_s = max(1, get_int("SAMPLE_INTERVAL_S", 10))
    threshold = get_int("ALERT_THRESHOLD", 12)
    fps = max(1, get_int("STREAM_FPS", 10))

    detect_cooldown_s = max(1, get_int("DETECT_COOLDOWN_S", 300))
    detect_save_dir = get_str("DETECT_SAVE_DIR", "ml/data/detections")

    knn_enabled = get_str("KNN_ENABLED", "true").lower() in {"1", "true", "yes", "y"}
    knn_model_path = get_str("KNN_MODEL_PATH", "ml/models/knn.joblib")
    knn_model = None
    if knn_enabled and knn_model is None and Path(knn_model_path).exists():
        try:
            from ml.app.knn import load_knn
            knn_model = load_knn(Path(knn_model_path))
            ctx.logger.info(f"KNN model loaded in worker: {knn_model_path}")
        except Exception as e:
            ctx.logger.error(f"Gagal memuat KNN di worker: {e}")

    cap = None
    while cap is None and not stop_event.is_set():
        cap = open_capture(src, backend, ctx.camera_status, ctx.logger)
        if cap is None:
            ctx.camera_status.update({
                "open": False, "src": src, "backend": backend,
                "last_error": f"Gagal membuka kamera: src={src} backend={backend}. Akan retry..."
            })
            ctx.logger.error(f"Gagal membuka kamera: src={src} backend={backend}. Retry 1s")
            time.sleep(1.0)

    if stop_event.is_set():
        return

    cap.set(cv2.CAP_PROP_FPS, fps)
    w = get_int("STREAM_WIDTH", 1280)
    h = get_int("STREAM_HEIGHT", 720)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

    fail_count = 0
    last_alert_ts = 0.0
    last_capture_ts = 0.0
    try:
        while not stop_event.is_set():
            ok, frame = cap.read()
            if not ok or frame is None:
                fail_count += 1
                ctx.camera_status.update({"open": False, "src": src, "backend": backend, "last_error": "Frame tidak terbaca"})
                time.sleep(0.1)
                if fail_count >= 30:
                    try:
                        cap.release()
                    except Exception:
                        pass
                    time.sleep(0.2)
                    cap = open_capture(src, backend, ctx.camera_status, ctx.logger)
                    if cap is None:
                        ctx.camera_status.update({"open": False, "src": src, "backend": backend, "last_error": "Re-open kamera gagal"})
                        time.sleep(0.5)
                        continue
                    cap.set(cv2.CAP_PROP_FPS, fps)
                    w = get_int("STREAM_WIDTH", 1280)
                    h = get_int("STREAM_HEIGHT", 720)
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
                continue

            raw_frame = frame.copy()
            gray_full = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.7
            thickness = 2
            color = (255, 255, 255)
            margin = 12

            # ROI dan metrik
            rx = get_int("ROI_X", 0)
            ry = get_int("ROI_Y", 0)
            rw = get_int("ROI_W", 0)
            rh = get_int("ROI_H", 0)
            if rw <= 0 or rh <= 0:
                rw, rh = frame.shape[1], frame.shape[0]

            # Face suppression sederhana (sesuai versi service)
            faces = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml") \
                .detectMultiScale(gray_full, scaleFactor=1.2, minNeighbors=5, minSize=(60, 60))
            frame_area = float(frame.shape[0] * frame.shape[1])
            face_area_pct = (sum(int(w*h) for _,_,w,h in faces) / frame_area) * 100.0 if faces is not None else 0.0
            person_suppress = get_int("PERSON_SUPPRESS", 1) != 0
            person_area_pct_threshold = get_int("PERSON_AREA_PCT", 5)
            suppressed = person_suppress and (face_area_pct >= person_area_pct_threshold)

            roi_img = raw_frame[ry:ry+rh, rx:rx+rw]
            trash_pct = 0.0
            if not suppressed:
                gray = cv2.cvtColor(roi_img, cv2.COLOR_BGR2GRAY)
                blur = cv2.GaussianBlur(gray, (5, 5), 0)
                _, thr = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                fg = cv2.morphologyEx(thr, cv2.MORPH_OPEN, kernel, iterations=1)
                trash_pct = (float(cv2.countNonZero(fg)) / float(fg.size)) * 100.0

            knn_label, knn_conf = None, None
            if knn_enabled and knn_model is not None and not suppressed:
                try:
                    from ml.app.knn import predict_knn
                    knn_label, knn_conf = predict_knn(knn_model, roi_img)
                except Exception as e:
                    ctx.logger.error(f"KNN infer error: {e}")

            is_trash = (trash_pct >= threshold) or (knn_label == "ADA_SAMPAH")
            text = f"Trash {round(trash_pct, 2)}%{' SUP' if suppressed else ''}"
            cv2.putText(frame, text, (margin, margin + 20), font, font_scale, color, thickness, cv2.LINE_AA)
            if rw > 0 and rh > 0 and (rw, rh) != (frame.shape[1], frame.shape[0]):
                cv2.rectangle(frame, (rx, ry), (rx + rw, ry + rh), (80, 80, 80), 2)

            ok_jpeg, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            if ok_jpeg:
                ctx.set_latest_jpeg(encoded.tobytes())
                ctx.update_metrics({
                    "trashPct": round(trash_pct, 2),
                    "ts": datetime.now().isoformat(),
                    "faces": int(len(faces)) if faces is not None else 0,
                    "suppressed": suppressed,
                    "cooldownActive": (time.time() - last_capture_ts) < detect_cooldown_s,
                    "knnLabel": knn_label,
                    "knnConfidence": knn_conf,
                })

            now = time.time()
            can_capture = (now - last_capture_ts) >= detect_cooldown_s
            if ctx.save_detections_getter() and is_trash and not suppressed and can_capture:
                ensure_dir(Path(detect_save_dir))
                out_path = Path(detect_save_dir) / f"trash_{timestamp_str()}.jpg"
                ok_save = cv2.imwrite(str(out_path), raw_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
                if ok_save:
                    last_capture_ts = now
                ctx.logger.info(
                    f"DETECTED: label={(knn_label if knn_label is not None else ('ADA_SAMPAH' if is_trash else 'BERSIH'))} "
                    f"trashPct={round(trash_pct, 2)} suppressed={suppressed} "
                    f"roi=({rx},{ry},{rw},{rh}) saved={'yes' if ok_save else 'no'} "
                    f"path={out_path if ok_save else None}"
                )

            if is_trash and not suppressed and (now - last_alert_ts) >= interval_s:
                last_alert_ts = now

            time.sleep(1.0 / fps)
    finally:
        try:
            if cap:
                cap.release()
        except Exception:
            pass
        ctx.logger.info("Camera worker stopped")