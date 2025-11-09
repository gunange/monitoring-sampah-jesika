# impor modul
import cv2, time
import threading
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from typing import Callable, Any
import requests

from ml.app.config import get_int, get_str
from ml.app.utils import ensure_dir, timestamp_str, get_logger
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
    # gunakan model KNN dari service; JANGAN load langsung dari file
    knn_model_getter = ctx.knn_model_getter
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

    # State: logging perubahan KNN dan penumpukan (log terpisah)
    trash_logger = get_logger("trash-info", Path("ml/logs/trash_info.log"))
    last_knn_label_logged = None
    accum_start_ts = None
    accum_notified = False
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

            # reset label setiap frame
            knn_label, knn_conf = None, 0.0

            # KNN hanya saat tidak suppressed
            if knn_enabled and not suppressed:
                knn_model = knn_model_getter()
                if knn_model is not None:
                    try:
                        from ml.app.knn import predict_knn
                        knn_label, knn_conf = predict_knn(knn_model, roi_img)
                    except Exception as e:
                        ctx.logger.error(f"KNN infer error: {e}")

            # === Fitur pra-KNN (definisikan sebelum dipakai di overlay) ===
            hsv_stats = {}
            lbp59 = []
            edge_den = 0.0
            shape_feats = {"area_ratio": 0.0, "solidity": 0.0, "hu7": [0.0]*7}
            try:
                from ml.app.image_features import (
                    hsv_hist_and_stats_bgr,
                    lbp_uniform_hist,
                    edge_density,
                    contour_features_from_mask,
                )
                hsv_stats = hsv_hist_and_stats_bgr(roi_img) or {}
                gray_roi = cv2.cvtColor(roi_img, cv2.COLOR_BGR2GRAY)
                lbp59 = lbp_uniform_hist(gray_roi) or []
                edge_den = edge_density(gray_roi)
                if not suppressed:
                    shape_feats = contour_features_from_mask(fg)
            except Exception as e:
                ctx.logger.warning(f"Pra-KNN feature error: {e}")

            # === Similarity ke dataset referensi (skip bila suppressed) ===
            sim_label, sim_top1, sim_topk = None, 0.0, 0.0
            try:
                from ml.app.reference import compute_similarity, has_reference
                if not suppressed and has_reference():
                    sim_label, sim_top1, sim_topk = compute_similarity(roi_img, knn_model, topk=5)
            except Exception as e:
                ctx.logger.warning(f"Similarity compute error: {e}")

            # Fusi KNN + Similarity: override jika KNN rendah tapi similarity kuat
            if not suppressed and knn_label in {"SAMPAH_MENUMPUK", "SAMPAH MENUMPUK"} and knn_conf < 0.7:
                if sim_label in {"ADA_SAMPAH", "ADA SAMPAH"} and sim_top1 >= 0.8:
                    knn_label = "ADA_SAMPAH"
                    knn_conf = float(sim_top1)
            # === Keputusan trash: HANYA berdasarkan KNN ===
            positive_labels = {"ADA_SAMPAH", "ADA SAMPAH", "SAMPAH MENUMPUK", "SAMPAH_MENUMPUK"}
            is_trash = (not suppressed) and (knn_label in positive_labels)

            # Normalisasi label (3 kelas) untuk log & dataset
            label_norm = "BERSIH"
            if not suppressed:
                if knn_label in {"SAMPAH MENUMPUK", "SAMPAH_MENUMPUK"}:
                    label_norm = "SAMPAH MENUMPUK"
                elif knn_label in {"ADA SAMPAH", "ADA_SAMPAH"}:
                    label_norm = "ADA SAMPAH"

            # === Log perubahan KNN dan kontrol penumpukan ===
            now_ts = time.time()
            if label_norm != last_knn_label_logged:
                prev = last_knn_label_logged
                trash_logger.info(
                    f"KNN_CHANGE: from={prev} to={label_norm} "
                    f"conf={round(knn_conf or 0.0, 3)} trashPct={round(trash_pct, 2)} "
                    f"suppressed={suppressed}"
                )
                # Masuk ke penumpukan
                if label_norm == "SAMPAH MENUMPUK" and not suppressed:
                    accum_start_ts = now_ts
                    accum_notified = False
                    trash_logger.info("ACCUM_START: SAMPAH MENUMPUK dimulai")
                else:
                    # Keluar dari penumpukan, reset
                    if accum_start_ts is not None:
                        duration = now_ts - accum_start_ts
                        trash_logger.info(f"ACCUM_END: durasi={round(duration,1)}s label_now={label_norm}")
                    accum_start_ts = None
                    accum_notified = False

                last_knn_label_logged = label_norm
            else:
                # Stabil: cek durasi hanya jika BELUM mengirim notifikasi
                if (
                    label_norm == "SAMPAH MENUMPUK"
                    and not suppressed
                    and accum_start_ts is not None
                    and not accum_notified
                ):
                    duration = now_ts - accum_start_ts
                    trash_logger.info(f"ACCUM_CHECK: durasi={round(duration,1)}s")
                    if duration >= 60:
                        try:
                            payload = {
                                "event": "SAMPAH_MENUMPUK",
                                "startedAt": datetime.fromtimestamp(accum_start_ts).isoformat(),
                                "durationSec": round(duration, 2),
                                "knnConfidence": round(knn_conf or 0.0, 4),
                                "trashPct": round(trash_pct, 2),
                            }
                            resp = requests.post("http://localhost:3101/api", json=payload, timeout=5)
                            trash_logger.info(f"ACCUM_NOTIFY_SENT: status={resp.status_code} payload={payload}")
                            # Hentikan cek sampai label berubah
                            accum_notified = True
                        except Exception as e:
                            trash_logger.error(f"ACCUM_NOTIFY_ERROR: {e}")
                else:
                    if accum_start_ts is not None:
                        duration = time.time() - accum_start_ts
                        trash_logger.info(f"ACCUM_END: durasi={round(duration,1)}s label_now={label_norm}")
                    accum_start_ts = None
                    accum_notified = False

                last_knn_label_logged = label_norm
            # Overlay utama
            text = f"Trash {round(trash_pct, 2)}%{' SUP' if suppressed else ''}"
            cv2.putText(frame, text, (margin, margin + 20), font, font_scale, color, thickness, cv2.LINE_AA)

            # Tampilkan KNN sesuai label (Python, bukan JS)
            if not suppressed and knn_label:
                if knn_label in {"SAMPAH_MENUMPUK", "SAMPAH MENUMPUK"}:
                    label_text = f"KNN: SAMPAH MENUMPUK ({round(knn_conf, 2)})"
                    label_color = (0, 0, 255)
                elif knn_label in {"ADA_SAMPAH", "ADA SAMPAH"}:
                    label_text = f"KNN: ADA SAMPAH ({round(knn_conf, 2)})"
                    label_color = (0, 128, 255)
                else:
                    label_text = f"KNN: BERSIH ({round(knn_conf, 2)})"
                    label_color = (0, 255, 0)
                cv2.putText(frame, label_text, (margin, margin + 40), font, font_scale, label_color, thickness, cv2.LINE_AA)

            # Tampilkan Similarity sebagai INFO saja (tidak mempengaruhi keputusan)
            if not suppressed and sim_label:
                sim_info = f"SIM: {sim_label} top1={round(sim_top1, 2)} avg5={round(sim_topk, 2)}"
                cv2.putText(frame, sim_info, (margin, margin + 60), font, font_scale, color, thickness, cv2.LINE_AA)

            # Overlay ringkasan fitur pra-KNN (HSV/LBP/Edge/Shape)
            y = margin + 86
            # HSV stats line
            if hsv_stats:
                cv2.putText(
                    frame,
                    f"HSV hist H32/S16/V8 | H[{round(hsv_stats.get('H_mean',0),1)},{round(hsv_stats.get('H_std',0),1)}] "
                    f"S[{round(hsv_stats.get('S_mean',0),1)},{round(hsv_stats.get('S_std',0),1)}] "
                    f"V[{round(hsv_stats.get('V_mean',0),1)},{round(hsv_stats.get('V_std',0),1)}]",
                    (margin, y), font, 0.6, color, 1, cv2.LINE_AA
                )
                y += 22
                # tampilkan beberapa bin awal untuk tiap histogram agar ringkas
                h_bins = hsv_stats.get("histH32", [])[:6]
                s_bins = hsv_stats.get("histS16", [])[:6]
                v_bins = hsv_stats.get("histV8", [])[:6]
                cv2.putText(frame, f"H[0:6]={[round(b,3) for b in h_bins]}", (margin, y), font, 0.6, color, 1, cv2.LINE_AA)
                y += 22
                cv2.putText(frame, f"S[0:6]={[round(b,3) for b in s_bins]}", (margin, y), font, 0.6, color, 1, cv2.LINE_AA)
                y += 22
                cv2.putText(frame, f"V[0:6]={[round(b,3) for b in v_bins]}", (margin, y), font, 0.6, color, 1, cv2.LINE_AA)
                y += 22
            # LBP, edge, shape
            if lbp59:
                cv2.putText(frame, f"LBP59[0:6]={[round(b,3) for b in lbp59[:6]]}", (margin, y), font, 0.6, color, 1, cv2.LINE_AA)
                y += 22
            cv2.putText(frame, f"Edge density={round(edge_den,3)}", (margin, y), font, 0.6, color, 1, cv2.LINE_AA)
            y += 22
            cv2.putText(frame, f"Shape area_ratio={round(shape_feats['area_ratio'],3)} solidity={round(shape_feats['solidity'],3)}", (margin, y), font, 0.6, color, 1, cv2.LINE_AA)
            y += 22

            if rw > 0 and rh > 0 and (rw, rh) != (frame.shape[1], frame.shape[0]):
                cv2.rectangle(frame, (rx, ry), (rx + rw, ry + rh), (80, 80, 80), 2)

            # Encode RAW frame and store to buffer for dataset capture
            ok_raw_jpeg, raw_encoded = cv2.imencode(".jpg", raw_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
            if ok_raw_jpeg:
                ctx.set_latest_raw_jpeg(raw_encoded.tobytes())

            # Overlay + metrics for preview
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
                    "similarityLabel": sim_label,
                    "similarityTop1": round(sim_top1, 6),
                    "similarityAvg5": round(sim_topk, 6),
                    # fitur pra-KNN untuk monitoring
                    "features": {
                        **(hsv_stats or {}),
                        "LBP59": lbp59,
                        "edge_density": round(edge_den, 6),
                        "area_ratio": round(shape_feats["area_ratio"], 6),
                        "solidity": round(shape_feats["solidity"], 6),
                        "hu7": shape_feats["hu7"],
                        "trashPct": round(trash_pct, 2),
                    }
                })

            now = time.time()
            can_capture = (now - last_capture_ts) >= detect_cooldown_s
            if ctx.save_detections_getter() and is_trash and not suppressed and can_capture:
                ensure_dir(Path(detect_save_dir))
                out_path = Path(detect_save_dir) / f"trash_{timestamp_str()}.jpg"
                ok_save = cv2.imwrite(str(out_path), raw_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
                if ok_save:
                    last_capture_ts = now
                # Normalisasi label untuk penyimpanan/dataset agar kompatibel
                det_label = "BERSIH"
                if knn_label in {"SAMPAH MENUMPUK", "SAMPAH_MENUMPUK"}:
                    det_label = "SAMPAH MENUMPUK"
                elif knn_label in {"ADA SAMPAH", "ADA_SAMPAH"} or (knn_label is None and is_trash):
                    det_label = "ADA SAMPAH"
                # log, simpan file, dll.
                ctx.logger.info(
                    f"DETECTED: label={det_label} "
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