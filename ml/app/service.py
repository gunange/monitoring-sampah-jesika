from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, Response, HTMLResponse
import cv2, threading, time, os, json
from pathlib import Path
import uuid
from datetime import datetime
import numpy as np

from .config import get_int, get_str
from .utils import get_logger, ensure_dir, timestamp_str
from ml.router.status_router import status_router
from ml.router.stream_router import stream_router
from ml.router.frame_router import frame_router
from ml.router.camera_router import camera_router
from ml.router.dataset_router import dataset_router
from ml.router.knn_router import knn_router

# module: service.py (deklarasi global)
app = FastAPI()
app.include_router(status_router)
app.include_router(stream_router)
app.include_router(frame_router)
app.include_router(camera_router)
app.include_router(dataset_router)
app.include_router(knn_router)

_latest_jpeg: bytes | None = None
_latest_raw_jpeg: bytes | None = None
_captured_raw_jpeg: bytes | None = None
_latest_metrics: dict = {"trashPct": 0.0, "ts": None}
_state_lock = threading.Lock()
_save_detections: bool = False
_knn_model = None

_worker_thread: threading.Thread | None = None
_worker_stop: threading.Event | None = None

logger = get_logger("ml-service", Path("ml/logs/ml_service.log"))

_camera_status: dict = {"open": False, "src": None, "backend": None, "last_error": None}

BACKENDS = {
    "ANY": int(cv2.CAP_ANY),
    "AVFOUNDATION": int(cv2.CAP_AVFOUNDATION),  # macOS
}

FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def parse_camera_src():
    s = get_str("CAMERA_SRC", "0")
    try:
        return int(s)
    except ValueError:
        return s

def open_capture(src, backend_name: str | None):
    tried = []
    def try_backend(name: str | None):
        cap = cv2.VideoCapture(src, BACKENDS.get(name.upper(), cv2.CAP_ANY)) if name else cv2.VideoCapture(src)
        label = name or "DEFAULT"
        tried.append(label)
        if cap is None or not cap.isOpened():
            try:
                if cap: cap.release()
            except Exception:
                pass
            return None
        ok, _ = cap.read()
        if not ok:
            try:
                cap.release()
            except Exception:
                pass
            return None
        _camera_status.update({"open": True, "src": src, "backend": label, "last_error": None})
        return cap

    cap = None
    if backend_name:
        cap = try_backend(backend_name)
    if cap is None:
        for name in ["AVFOUNDATION", "ANY", None]:
            if backend_name and (name == backend_name or (name is None and backend_name is None)):
                continue
            cap = try_backend(name)
            if cap:
                break

    if cap is None:
        _camera_status.update({
            "open": False,
            "src": src,
            "backend": backend_name,
            "last_error": f"OpenCV gagal membuka kamera. Dicoba: {tried}. Periksa izin kamera & apakah sedang dipakai app lain."
        })
        return None
    return cap

def get_roi(frame):
    h, w = frame.shape[:2]
    x = max(0, get_int("ROI_X", 0))
    y = max(0, get_int("ROI_Y", 0))
    rw = get_int("ROI_W", 0)
    rh = get_int("ROI_H", 0)
    if rw > 0 and rh > 0:
        rw = min(rw, w - x)
        rh = min(rh, h - y)
        return frame[y:y+rh, x:x+rw], (x, y, rw, rh)
    return frame, (0, 0, w, h)

def compute_trash_pct(frame) -> float:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thr = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    fg = cv2.morphologyEx(thr, cv2.MORPH_OPEN, kernel, iterations=1)
    return (float(cv2.countNonZero(fg)) / float(fg.size)) * 100.0

def compute_metrics(frame):
    roi_frame, (rx, ry, rw, rh) = get_roi(frame)
    gray_full = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = FACE_CASCADE.detectMultiScale(gray_full, scaleFactor=1.2, minNeighbors=5, minSize=(60, 60))
    frame_area = float(frame.shape[0] * frame.shape[1])
    face_area_pct = (sum(int(w*h) for _,_,w,h in faces) / frame_area) * 100.0 if faces is not None else 0.0

    person_suppress = get_int("PERSON_SUPPRESS", 1) != 0
    person_area_pct_threshold = get_int("PERSON_AREA_PCT", 5)

    suppressed = person_suppress and (face_area_pct >= person_area_pct_threshold)
    trash_pct = 0.0 if suppressed else compute_trash_pct(roi_frame)

    return {
        "trash_pct": trash_pct,
        "suppressed": suppressed,
        "faces": int(len(faces)) if faces is not None else 0,
        "face_area_pct": round(face_area_pct, 2),
        "roi": (rx, ry, rw, rh),
    }

# Helpers: ensure detection dirs/json exist, decode JPEG, and extract numeric features

def get_detection_dir() -> Path:
    return Path(get_str("DETECT_SAVE_DIR", "ml/data/detections"))

def get_dataset_json() -> Path:
    return get_detection_dir() / "dataset.json"

def ensure_detection_dirs():
    try:
        detect_dir = get_detection_dir()
        ensure_dir(detect_dir)
        dj = get_dataset_json()
        if not dj.exists():
            dj.write_text("[]", encoding="utf-8")
    except Exception as e:
        logger.error(f"ensure_detection_dirs error: {e}")


def decode_jpeg_to_bgr(jpeg_bytes: bytes):
    try:
        arr = np.frombuffer(jpeg_bytes, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return img
    except Exception:
        return None


def extract_features_bgr(img):
    try:
        h, w = img.shape[:2]
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Color histograms (H, S, V), 16 bins each, normalized
        hist_h = cv2.calcHist([hsv], [0], None, [16], [0, 180]).flatten()
        hist_s = cv2.calcHist([hsv], [1], None, [16], [0, 256]).flatten()
        hist_v = cv2.calcHist([hsv], [2], None, [16], [0, 256]).flatten()
        for hist in (hist_h, hist_s, hist_v):
            s = float(hist.sum()) or 1.0
            hist /= s

        # Color statistics
        h_mean = float(hsv[:, :, 0].mean()); h_std = float(hsv[:, :, 0].std())
        s_mean = float(hsv[:, :, 1].mean()); s_std = float(hsv[:, :, 1].std())
        v_mean = float(hsv[:, :, 2].mean()); v_std = float(hsv[:, :, 2].std())

        # Texture: Laplacian variance
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        lap = cv2.Laplacian(gray, cv2.CV_64F)
        lap_var = float(lap.var())

        # Edge ratio
        edges = cv2.Canny(img, 100, 200)
        edge_ratio = float(np.count_nonzero(edges)) / float(h * w) if (h * w) > 0 else 0.0

        # Shape: largest contour area ratio (Otsu threshold)
        _, thr = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        cnts = cv2.findContours(thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = cnts[0] if len(cnts) == 2 else cnts[1]
        max_area = float(max((cv2.contourArea(c) for c in contours), default=0.0))
        shape_area_ratio = (max_area / float(h * w)) if (h * w) > 0 else 0.0

        return {
            "width": int(w),
            "height": int(h),
            "color_hist_h": hist_h.tolist(),
            "color_hist_s": hist_s.tolist(),
            "color_hist_v": hist_v.tolist(),
            "h_mean": h_mean, "h_std": h_std,
            "s_mean": s_mean, "s_std": s_std,
            "v_mean": v_mean, "v_std": v_std,
            "laplacian_var": lap_var,
            "edge_ratio": edge_ratio,
            "shape_area_ratio": shape_area_ratio,
        }
    except Exception as e:
        logger.error(f"extract_features_bgr error: {e}")
        return None

def camera_worker(stop_event: threading.Event):
    global _knn_model
    src = parse_camera_src()
    backend = get_str("CAMERA_BACKEND", "AVFOUNDATION")
    interval_s = max(1, get_int("SAMPLE_INTERVAL_S", 10))
    threshold = get_int("ALERT_THRESHOLD", 12)
    fps = max(1, get_int("STREAM_FPS", 10))

    detect_cooldown_s = max(1, get_int("DETECT_COOLDOWN_S", 300))
    detect_save_dir = get_str("DETECT_SAVE_DIR", "ml/data/detections")

    knn_enabled = get_str("KNN_ENABLED", "true").lower() in {"1", "true", "yes", "y"}
    knn_model_path = get_str("KNN_MODEL_PATH", "ml/models/knn.joblib")
    if knn_enabled and _knn_model is None and Path(knn_model_path).exists():
        try:
            from .knn import load_knn
            _knn_model = load_knn(Path(knn_model_path))
            logger.info(f"KNN model loaded in worker: {knn_model_path}")
        except Exception as e:
            logger.error(f"Gagal memuat KNN di worker: {e}")
    # HAPUS: detections_json = get_str("DETECTIONS_JSON", "ml/logs/detections.json")

    cap = None
    while cap is None and not stop_event.is_set():
        cap = open_capture(src, backend)
        if cap is None:
            _camera_status.update({
                "open": False,
                "src": src,
                "backend": backend,
                "last_error": f"Gagal membuka kamera: src={src} backend={backend}. Akan retry..."
            })
            logger.error(f"Gagal membuka kamera: src={src} backend={backend}. Retry 1s")
            time.sleep(1.0)

    if stop_event.is_set():
        return

    cap.set(cv2.CAP_PROP_FPS, fps)

    fail_count = 0
    last_alert_ts = 0.0
    last_capture_ts = 0.0
    try:
        while not stop_event.is_set():
            ok, frame = cap.read()
            if not ok or frame is None:
                fail_count += 1
                _camera_status.update({"open": False, "src": src, "backend": backend, "last_error": "Frame tidak terbaca"})
                time.sleep(0.1)
                if fail_count >= 30:
                    try:
                        cap.release()
                    except Exception:
                        pass
                    time.sleep(0.2)
                    cap = open_capture(src, backend)
                    if cap is None:
                        _camera_status.update({"open": False, "src": src, "backend": backend, "last_error": "Re-open kamera gagal"})
                        time.sleep(0.5)
                        continue
                    cap.set(cv2.CAP_PROP_FPS, fps)
                    fail_count = 0
                continue
            else:
                if fail_count:
                    fail_count = 0
                _camera_status.update({"open": True, "src": src, "backend": backend, "last_error": None})

            raw_frame = frame.copy()
            ok_raw, raw_jpeg = cv2.imencode(".jpg", raw_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
            if ok_raw:
                with _state_lock:
                    _latest_raw_jpeg = raw_jpeg.tobytes()

            m = compute_metrics(frame)
            trash_pct = m["trash_pct"]
            suppressed = m["suppressed"]
            rx, ry, rw, rh = m["roi"]

            knn_label, knn_conf = None, None
            if _knn_model is not None and not suppressed:
                try:
                    roi_img = raw_frame[ry:ry+rh, rx:rx+rw] if rw > 0 and rh > 0 else raw_frame
                    from .knn import predict_knn
                    knn_label, knn_conf = predict_knn(_knn_model, roi_img)
                except Exception as e:
                    logger.error(f"KNN infer error: {e}")

            is_trash = False
            if suppressed:
                is_trash = False
            elif knn_label is not None:
                is_trash = (knn_label == "ADA_SAMPAH")
            else:
                is_trash = trash_pct >= threshold

            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.0
            thickness = 2
            if suppressed:
                status_text = "Orang terdeteksi — deteksi sampah dinonaktifkan"
                color = (255, 255, 0)
            else:
                if knn_label is not None:
                    status_text = f"KNN: {knn_label}"
                    if knn_conf is not None:
                        status_text += f" ({knn_conf:.2f})"
                else:
                    status_text = "Ada sampah tertumpuk" if is_trash else "Kondisi normal"
                color = (0, 0, 255) if is_trash else (0, 200, 0)
            text = f"{status_text} • {trash_pct:.2f}%"
            margin = 12
            (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
            cv2.rectangle(frame, (margin - 6, margin - 6), (margin + text_w + 6, margin + text_h + 6), (0, 0, 0), -1)
            cv2.putText(frame, text, (margin, margin + text_h), font, font_scale, color, thickness, cv2.LINE_AA)

            if rw > 0 and rh > 0 and (rw, rh) != (frame.shape[1], frame.shape[0]):
                cv2.rectangle(frame, (rx, ry), (rx + rw, ry + rh), (80, 80, 80), 2)

            ok_jpeg, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            if ok_jpeg:
                with _state_lock:
                    _latest_jpeg = encoded.tobytes()
                    _latest_metrics["trashPct"] = round(trash_pct, 2)
                    _latest_metrics["ts"] = datetime.now().isoformat()
                    _latest_metrics["faces"] = m["faces"]
                    _latest_metrics["suppressed"] = suppressed
                    _latest_metrics["cooldownActive"] = (time.time() - last_capture_ts) < detect_cooldown_s
                    _latest_metrics["knnLabel"] = knn_label
                    _latest_metrics["knnConfidence"] = knn_conf

            now = time.time()
            can_capture = (now - last_capture_ts) >= detect_cooldown_s
            if _save_detections and is_trash and not suppressed and can_capture:
                ensure_dir(Path(detect_save_dir))
                out_path = Path(detect_save_dir) / f"trash_{timestamp_str()}.jpg"
                ok_save = cv2.imwrite(str(out_path), raw_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
                if ok_save:
                    last_capture_ts = now

                # Ganti penulisan JSON dengan logging biasa
                logger.info(
                    f"DETECTED: label={(knn_label if knn_label is not None else ('ADA_SAMPAH' if is_trash else 'BERSIH'))} "
                    f"trashPct={round(trash_pct, 2)} suppressed={suppressed} "
                    f"roi=({rx},{ry},{rw},{rh}) saved={'yes' if ok_save else 'no'} "
                    f"path={out_path if ok_save else None}"
                )
                try:
                    ensure_dir(Path(detections_json).parent)
                    event = {
                        "ts": datetime.now().isoformat(),
                        "label": knn_label if knn_label is not None else ("ADA_SAMPAH" if is_trash else "BERSIH"),
                        "knnConfidence": knn_conf,
                        "trashPct": round(trash_pct, 2),
                        "suppressed": suppressed,
                        "roi": {"x": rx, "y": ry, "w": rw, "h": rh},
                        "imagePath": str(out_path) if ok_save else None,
                    }
                    if Path(detections_json).exists():
                        try:
                            data = json.loads(Path(detections_json).read_text())
                            if not isinstance(data, list):
                                data = []
                        except Exception:
                            data = []
                    else:
                        data = []
                    data.append(event)
                    Path(detections_json).write_text(json.dumps(data, indent=2))
                    logger.info(f"DETECTED(JSON): {event}")
                except Exception as e:
                    logger.error(f"Gagal menulis JSON: {e}")

            if is_trash and not suppressed and (now - last_alert_ts) >= interval_s:
                last_alert_ts = now

            time.sleep(1.0 / fps)
    finally:
        try:
            if cap:
                cap.release()
        except Exception:
            pass
        logger.info("Camera worker stopped")

def start_worker():
    global _worker_thread, _worker_stop
    if _worker_stop:
        _worker_stop.set()
        time.sleep(0.5)
    _worker_stop = threading.Event()
    _worker_thread = threading.Thread(target=camera_worker, args=(_worker_stop,), daemon=True)
    _worker_thread.start()

@app.on_event("startup")
def on_startup():
    logger.info("Startup: kamera tidak dibuka otomatis. Gunakan tombol Mulai Kamera.")
    try:
        if get_str("KNN_ENABLED", "true").lower() in {"1","true","yes","y"}:
            p = Path(get_str("KNN_MODEL_PATH", "ml/models/knn.joblib"))
            if p.exists():
                from .knn import load_knn
                global _knn_model
                _knn_model = load_knn(p)
                logger.info(f"Startup: KNN model loaded {p}")
    except Exception as e:
        logger.error(f"Startup: gagal memuat KNN: {e}")

@app.on_event("shutdown")
def on_shutdown():
    if _worker_stop:
        _worker_stop.set()
    logger.info("Shutdown signal sent")

@app.get("/")
def root():
    with _state_lock:
        return {"service": "ml-service", "status": "ok", "metrics": _latest_metrics}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/config")
def config():
    return {
        "CAMERA_SRC": get_str("CAMERA_SRC", "0"),
        "CAMERA_BACKEND": get_str("CAMERA_BACKEND", "AVFOUNDATION"),
        "STREAM_FPS": get_int("STREAM_FPS", 10),
        "SAMPLE_INTERVAL_S": get_int("SAMPLE_INTERVAL_S", 10),
        "ALERT_THRESHOLD": get_int("ALERT_THRESHOLD", 12),
        "PERSON_SUPPRESS": get_int("PERSON_SUPPRESS", 1),
        "PERSON_AREA_PCT": get_int("PERSON_AREA_PCT", 5),
        "ROI_X": get_int("ROI_X", 0),
        "ROI_Y": get_int("ROI_Y", 0),
        "ROI_W": get_int("ROI_W", 0),
        "ROI_H": get_int("ROI_H", 0),
        "DETECT_COOLDOWN_S": get_int("DETECT_COOLDOWN_S", 300),
        "DETECT_SAVE_DIR": get_str("DETECT_SAVE_DIR", "ml/data/detections"),
        "KNN_ENABLED": get_str("KNN_ENABLED", "true"),
        "KNN_MODEL_PATH": get_str("KNN_MODEL_PATH", "ml/models/knn.joblib"),
        "KNN_NEIGHBORS": get_int("KNN_NEIGHBORS", 5),
    }

def mjpeg_from_latest():
    boundary = b"--frame\r\n"
    while True:
        with _state_lock:
            frame_bytes = _latest_jpeg or _latest_raw_jpeg
            cam = dict(_camera_status)
        if frame_bytes:
            yield (boundary +
                   b"Content-Type: image/jpeg\r\n" +
                   b"Content-Length: " + str(len(frame_bytes)).encode() + b"\r\n\r\n" +
                   frame_bytes + b"\r\n")
        else:
            placeholder = np.zeros((360, 640, 3), dtype=np.uint8)
            msgs = ["Waiting for camera..."]
            if not cam.get("open"):
                msgs.append(f"Not opened (src={cam.get('src')}, backend={cam.get('backend')})")
            if cam.get("last_error"):
                msgs.append(f"Error: {cam.get('last_error')}")
            y = 150
            for m in msgs:
                cv2.putText(placeholder, m, (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
                y += 30
            ok, buf = cv2.imencode(".jpg", placeholder, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            if ok:
                ph = buf.tobytes()
                yield (boundary +
                       b"Content-Type: image/jpeg\r\n" +
                       b"Content-Length: " + str(len(ph)).encode() + b"\r\n\r\n" +
                       ph + b"\r\n")
        time.sleep(0.2)

@app.get("/status")
def status():
    with _state_lock:
        metrics = dict(_latest_metrics)
    st = dict(_camera_status)
    st["saveDetections"] = _save_detections
    return {"camera": st, "metrics": metrics}

@app.post("/camera")
def set_camera(payload: dict):
    src = str(payload.get("src", "0"))
    backend = str(payload.get("backend", "AVFOUNDATION"))
    save_dets = bool(payload.get("saveDetections", False))
    os.environ["CAMERA_SRC"] = src
    os.environ["CAMERA_BACKEND"] = backend
    global _save_detections
    _save_detections = save_dets
    logger.info(f"Set camera requested: src={src}, backend={backend}, saveDetections={save_dets}. Restarting worker.")
    start_worker()
    return {"ok": True, "src": src, "backend": backend, "saveDetections": save_dets}

@app.get("/frame")
def frame():
    with _state_lock:
        frame_bytes = _latest_jpeg or _latest_raw_jpeg
    if not frame_bytes:
        return Response(status_code=204)
    return Response(content=frame_bytes, media_type="image/jpeg")

@app.get("/frame/raw")
def frame_raw():
    with _state_lock:
        frame_bytes = _latest_raw_jpeg
    if not frame_bytes:
        return Response(status_code=204)
    return Response(content=frame_bytes, media_type="image/jpeg")

@app.get("/stream")
def stream():
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Connection": "keep-alive",
    }
    return StreamingResponse(
        mjpeg_from_latest(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers=headers,
    )

@app.get("/stream/html")
def stream_html():
    return HTMLResponse(
        """
        <!doctype html><html><head><meta charset="utf-8"><title>ML Stream</title>
          <style>
            body{margin:0;background:#111;height:100vh;color:#ddd;font-family:system-ui}
            .wrap{display:flex;align-items:center;justify-content:center;height:80vh}
            img{max-width:96vw;max-height:70vh;border:8px solid #333;border-radius:8px;box-shadow:0 10px 30px rgba(0,0,0,.5)}
            .toolbar{display:flex;gap:8px;align-items:center;justify-content:center;padding:10px}
            button{background:#444;color:#fff;border:none;padding:8px 12px;border-radius:6px;cursor:pointer}
            button.primary{background:#0a7}
            button.danger{background:#c33}
            .badge{position:fixed;top:14px;left:14px;background:#222;color:#ddd;padding:6px 10px;border-radius:6px}
            .note{font-size:12px;color:#aaa;text-align:center;margin-top:6px}
          </style>
        </head>
        <body>
          <div class="badge">Stream Kamera</div>
          <div class="wrap"><img id="img" src="/stream" /></div>
          <div class="toolbar">
            <button id="startCam" class="primary">Mulai Kamera</button>
            <span id="dsInfo"></span>
          </div>
          <div class="note">Halaman melihat stream langsung.</div>
          <script>
            const dsInfo = document.getElementById('dsInfo');
            async function refreshStatus(){
              const st = await (await fetch('/status')).json();
              dsInfo.textContent = `Camera open=${st.camera.open} backend=${st.camera.backend || '-'} error=${st.camera.last_error || '-'}`;
            }
            refreshStatus();
            document.getElementById('startCam').onclick = async () => {
              await fetch('/camera', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({src:'0', backend:'AVFOUNDATION'})});
              setTimeout(async () => {
                const st = await (await fetch('/status')).json();
                if (!st.camera.open) {
                  await fetch('/camera', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({src:'0', backend:'ANY'})});
                }
                refreshStatus();
              }, 600);
            };
          </script>
        </body></html>
        """
    )

# Capture-based dataset flow
# Tangkap satu gambar dari kamera (on-demand, tanpa stream)
@app.post("/capture")
def capture(payload: dict = {}):
    global _captured_raw_jpeg
    # Prioritas: jika preview worker aktif, ambil dari buffer live
    with _state_lock:
        live = _latest_raw_jpeg
    if live:
        with _state_lock:
            _captured_raw_jpeg = live
        return {"ok": True, "source": "buffer"}
    # Warm-up capture jika belum ada preview
    src = parse_camera_src()
    backend = str(payload.get("backend", get_str("CAMERA_BACKEND", "AVFOUNDATION")))
    cap = open_capture(src, backend)
    if cap is None:
        return {"ok": False, "error": _camera_status.get("last_error") or "Tidak bisa membuka kamera"}
    try:
        warm_frames = max(10, get_int("CAPTURE_WARM_FRAMES", 15))
        for _ in range(warm_frames):
            ok_w, _ = cap.read()
            if not ok_w:
                break
            time.sleep(0.02)
        ok, frame = cap.read()
    finally:
        try:
            cap.release()
        except Exception:
            pass
    if not ok or frame is None:
        return {"ok": False, "error": "Gagal mengambil gambar dari kamera"}
    ok_raw, raw_jpeg = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    if not ok_raw:
        return {"ok": False, "error": "Gagal meng-encode JPEG"}
    with _state_lock:
        _captured_raw_jpeg = raw_jpeg.tobytes()
    return {"ok": True, "source": "direct"}

@app.get("/capture/image")
def capture_image():
    with _state_lock:
        b = _captured_raw_jpeg
    if not b:
        return Response(status_code=204)
    return Response(content=b, media_type="image/jpeg")

@app.post("/capture/reset")
def capture_reset():
    global _captured_raw_jpeg
    with _state_lock:
        _captured_raw_jpeg = None
    return {"ok": True}

@app.post("/camera/stop")
def camera_stop():
    global _worker_stop
    if _worker_stop:
        _worker_stop.set()
        time.sleep(0.3)
    return {"ok": True}

@app.get("/dataset")
def dataset_html():
    return HTMLResponse(
        """
        <!doctype html><html><head><meta charset="utf-8"><title>Dataset Latih</title>
          <style>
            body{margin:0;background:#111;color:#ddd;font-family:system-ui}
            .wrap{display:flex;align-items:center;justify-content:center;height:72vh}
            img{max-width:96vw;max-height:66vh;border:8px solid #333;border-radius:8px;box-shadow:0 10px 30px rgba(0,0,0,.5)}
            .toolbar{display:flex;gap:10px;align-items:center;justify-content:center;padding:12px;flex-wrap:wrap}
            button{background:#444;color:#fff;border:none;padding:8px 12px;border-radius:6px;cursor:pointer}
            button.primary{background:#0a7}
            button.danger{background:#c33}
            .badge{position:fixed;top:14px;left:14px;background:#222;color:#ddd;padding:6px 10px;border-radius:6px}
            .note{font-size:12px;color:#aaa;text-align:center;margin-top:6px}
            input[type=file]{color:#ddd}
          </style>
        </head>
        <body>
          <div class="badge">Dataset Latih</div>
          <div class="wrap">
            <div id="placeholder" style="width:85vw;height:60vh;background:#000;display:flex;align-items:center;justify-content:center;color:#ddd;border:8px solid #333;border-radius:8px;box-shadow:0 10px 30px rgba(0,0,0,.5)">Belum ada gambar. Tekan Ambil Gambar atau Stay Cam.</div>
            <img id="img" style="display:none" alt="capture" />
          </div>
          <div class="toolbar">
            <button id="btnStayCam">Stay Cam</button>
            <button id="btnStopCam">Stop Cam</button>
            <button id="btnCapture" class="primary">Ambil Gambar</button>
            <button id="btnReset">Reset</button>
            <button id="saveBersih">Simpan BERSIH</button>
            <button id="saveSampah" class="danger">Simpan ADA SAMPAH</button>
            <div style="margin-top:12px;">
              <input type="file" id="fileInput" accept="image/*" />
              <button id="uploadBersih">Upload BERSIH</button>
              <button id="uploadSampah" class="danger">Upload ADA SAMPAH</button>
            </div>
            <span id="dsInfo"></span>
          </div>
          <div class="note">Gunakan Stay Cam agar kamera siap (eksposur stabil), lalu Ambil Gambar. Simpan jika sudah sesuai, atau unggah file yang sudah ada.</div>
          <script>
            const dsInfo = document.getElementById('dsInfo');
            const img = document.getElementById('img');
            const placeholder = document.getElementById('placeholder');

            function showImage() {
              img.style.display = '';
              placeholder.style.display = 'none';
            }
            function showPlaceholder() {
              img.style.display = 'none';
              placeholder.style.display = '';
            }

            async function refreshDataset() {
              const s = await (await fetch('/dataset/status')).json();
              const k = await (await fetch('/knn/status')).json();
              dsInfo.textContent = `Dataset: BERSIH=${s.BERSIH} • ADA_SAMPAH=${s.ADA_SAMPAH} • KNN loaded=${k.loaded}`;
            }
            refreshDataset();

            let usingRawFallback = false;
            let rawTimer = null;

            function attachStream() {
              usingRawFallback = false;
              if (rawTimer) { clearInterval(rawTimer); rawTimer = null; }
              img.src = '/stream?ts=' + Date.now();
              showImage();
            }

            function attachRawFallback() {
              if (usingRawFallback) return;
              usingRawFallback = true;
              img.src = '/frame/raw?ts=' + Date.now();
              showImage();
              if (rawTimer) clearInterval(rawTimer);
              rawTimer = setInterval(() => {
                img.src = '/frame/raw?ts=' + Date.now();
              }, 250);
            }

            document.getElementById('btnStayCam').onclick = async () => {
              await fetch('/camera', {method:'POST', headers:{'Content-Type':'application/json'},
                body: JSON.stringify({src:'0', backend:'AVFOUNDATION', saveDetections:false})});
              await new Promise(r => setTimeout(r, 500));
              attachStream();
            };

            document.getElementById('btnStopCam').onclick = async () => {
              await fetch('/camera/stop', {method:'POST'});
              if (rawTimer) { clearInterval(rawTimer); rawTimer = null; }
              showPlaceholder();
            };

            document.getElementById('btnCapture').onclick = async () => {
              let r = await fetch('/capture', {method:'POST', headers:{'Content-Type':'application/json'},
                body: JSON.stringify({backend:'AVFOUNDATION'})});
              let j = await r.json();
              if (!j.ok) {
                r = await fetch('/capture', {method:'POST', headers:{'Content-Type':'application/json'},
                  body: JSON.stringify({backend:'ANY'})});
                j = await r.json();
              }
              if (!j.ok) {
                alert('Gagal ambil gambar: ' + (j.error || 'unknown'));
                return;
              }
              img.src = '/capture/image?ts=' + Date.now();
              showImage();
            };

            document.getElementById('btnReset').onclick = async () => {
              await fetch('/capture/reset', {method:'POST'});
              showPlaceholder();
            };

            async function saveLabel(label) {
              const r = await fetch('/dataset/add', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({label})});
              const j = await r.json();
              alert(j.ok ? `Tersimpan: ${j.path}` : `Gagal: ${j.error || 'unknown'}`);
              refreshDataset();
            }
            document.getElementById('saveBersih').onclick = () => saveLabel('BERSIH');
            document.getElementById('saveSampah').onclick = () => saveLabel('ADA_SAMPAH');

            async function uploadFiles(label) {
              const fi = document.getElementById('fileInput');
              if (!fi.files || fi.files.length === 0) {
                alert('Pilih file gambar terlebih dahulu');
                return;
              }
              const file = fi.files[0];
              try {
                const r = await fetch('/dataset/upload?label=' + encodeURIComponent(label), {
                  method: 'POST',
                  headers: { 'Content-Type': file.type || 'application/octet-stream' },
                  body: file
                });
                const j = await r.json();
                alert(j.ok ? `Upload tersimpan: ${j.file || j.path}` : `Gagal: ${j.error || 'unknown'}`);
                refreshDataset();
              } catch (e) {
                alert('Upload error: ' + e);
              }
            }
            document.getElementById('uploadBersih').onclick = () => uploadFiles('BERSIH');
            document.getElementById('uploadSampah').onclick = () => uploadFiles('ADA SAMPAH');
            document.getElementById('fileInput').addEventListener('change', (e) => {
              const file = e.target.files && e.target.files[0];
              if (file) {
                img.src = URL.createObjectURL(file);
                showImage();
              }
            });
          </script>
        </body></html>
        """
    )

@app.get("/dataset/status")
def dataset_status():
    return dataset_counts()

@app.post("/dataset/upload")
async def dataset_upload(request: Request, label: str = ""):
    ensure_detection_dirs()

    # Normalisasi label (dari query string)
    raw_label = (label or "").strip().upper()
    if raw_label in {"CLEAN", "BERSIH"}:
        norm_label = "BERSIH"
    elif raw_label in {"TRASH", "ADA SAMPAH", "ADA_SAMPAH", "SAMPAH"}:
        norm_label = "ADA SAMPAH"
    else:
        return {"ok": False, "error": "Label harus BERSIH atau ADA SAMPAH"}

    # Baca body biner
    try:
        file_bytes = await request.body()
    except Exception as e:
        return {"ok": False, "error": f"Gagal membaca body: {e}"}
    if not file_bytes:
        return {"ok": False, "error": "Body kosong; kirim gambar sebagai biner."}

    # Tentukan ekstensi dari Content-Type
    ct = (request.headers.get("content-type") or "").lower()
    ext = ".jpg"
    if ct.startswith("image/"):
        if "jpeg" in ct or "jpg" in ct:
            ext = ".jpg"
        elif "png" in ct:
            ext = ".png"
        elif "bmp" in ct:
            ext = ".bmp"
        elif "webp" in ct:
            ext = ".webp"
    elif ct == "application/octet-stream":
        ext = ".jpg"

    # Simpan file
    detect_dir = get_detection_dir()
    ensure_dir(detect_dir)
    ts = datetime.utcnow().isoformat(timespec="milliseconds") + "Z"
    short_id = uuid.uuid4().hex[:8]
    safe_label = norm_label.lower().replace(" ", "_")
    filename = f"{ts.replace(':','').replace('.','').replace('-','')}_{safe_label}_{short_id}{ext}"
    out_path = detect_dir / filename
    try:
        with open(out_path, "wb") as f:
            f.write(file_bytes)
    except Exception as e:
        return {"ok": False, "error": f"Gagal menyimpan gambar: {e}"}

    # Ekstraksi fitur numerik
    features = None
    try:
        bgr = decode_jpeg_to_bgr(file_bytes)
        if bgr is None:
            bgr = cv2.imdecode(np.frombuffer(file_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
        if bgr is not None:
            features = extract_features_bgr(bgr)
    except Exception as e:
        logger.warning(f"Gagal ekstraksi fitur: {e}")

    entry = {
        "id": uuid.uuid4().hex,
        "filename": filename,
        "label": norm_label,
        "timestamp": ts,
        "features": features,
    }

    # Append ke dataset.json
    dj = get_dataset_json()
    try:
        with _state_lock:
            data = []
            if dj.exists():
                try:
                    data = json.loads(dj.read_text(encoding="utf-8"))
                    if not isinstance(data, list):
                        data = []
                except Exception:
                    data = []
            data.append(entry)
            dj.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        return {"ok": False, "error": f"Gagal menulis dataset.json: {e}"}

    # Hitung ringkas untuk feedback
    bersih = sum(1 for x in data if str(x.get("label", "")).strip().upper() == "BERSIH")
    sampah = sum(1 for x in data if str(x.get("label", "")).strip().upper() in {"ADA SAMPAH", "ADA_SAMPAH"})
    return {
        "ok": True,
        "file": str(out_path),
        "entry": entry,
        "count": {"BERSIH": bersih, "ADA_SAMPAH": sampah, "TOTAL": bersih + sampah},
        "message": "Upload tersimpan ke ml/data/detections dan dataset.json",
    }

@app.post("/dataset/add")
def dataset_add(payload: dict = {}):
    label = str(payload.get("label") or payload.get("kelas") or "").strip().upper()
    if raw_label in {"CLEAN", "BERSIH"}:
        label = "BERSIH"
    elif raw_label in {"TRASH", "ADA SAMPAH", "ADA_SAMPAH", "SAMPAH"}:
        label = "ADA SAMPAH"
    else:
        return {"ok": False, "error": "Label harus BERSIH atau ADA SAMPAH"}

    with _state_lock:
        jpeg_bytes = _captured_raw_jpeg
    if not jpeg_bytes:
        return {"ok": False, "error": "Belum ada gambar yang ditangkap. Tekan Ambil Gambar dulu."}

    detect_dir = get_detection_dir()
    ensure_dir(detect_dir)
    ts = datetime.utcnow().isoformat(timespec="milliseconds") + "Z"
    short_id = uuid.uuid4().hex[:8]
    safe_label = label.lower().replace(" ", "_")
    filename = f"{ts.replace(':','').replace('.','').replace('-','')}_{safe_label}_{short_id}.jpg"
    out_path = detect_dir / filename

    try:
        with open(out_path, "wb") as f:
            f.write(jpeg_bytes)
    except Exception as e:
        return {"ok": False, "error": f"Gagal menyimpan gambar: {e}"}

    img = decode_jpeg_to_bgr(jpeg_bytes)
    if img is None:
        return {"ok": False, "error": "Gagal memuat JPEG untuk ekstraksi fitur."}
    features = extract_features_bgr(img)

    entry = {
        "id": uuid.uuid4().hex,
        "filename": filename,
        "label": label,
        "timestamp": ts,
        "features": features,
    }

    dj = get_dataset_json()
    try:
        with _state_lock:
            data = []
            if dj.exists():
                try:
                    data = json.loads(dj.read_text(encoding="utf-8"))
                    if not isinstance(data, list):
                        data = []
                except Exception:
                    data = []
            data.append(entry)
            dj.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        return {"ok": False, "error": f"Gagal menulis dataset.json: {e}"}

    return {
        "ok": True,
        "file": str(out_path),
        "entry": entry,
        "count": len(data),
        "message": "Gambar dan fitur tersimpan ke ml/data/detections/dataset.json",
    }

def start_worker():
    global _worker_thread, _worker_stop
    if _worker_stop:
        _worker_stop.set()
        time.sleep(0.5)
    _worker_stop = threading.Event()
    _worker_thread = threading.Thread(target=camera_worker, args=(_worker_stop,), daemon=True)
    _worker_thread.start()

@app.on_event("startup")
def on_startup():
    logger.info("Startup: kamera tidak dibuka otomatis. Gunakan tombol Mulai Kamera.")
    try:
        if get_str("KNN_ENABLED", "true").lower() in {"1","true","yes","y"}:
            p = Path(get_str("KNN_MODEL_PATH", "ml/models/knn.joblib"))
            if p.exists():
                from .knn import load_knn
                global _knn_model
                _knn_model = load_knn(p)
                logger.info(f"Startup: KNN model loaded {p}")
    except Exception as e:
        logger.error(f"Startup: gagal memuat KNN: {e}")

@app.on_event("shutdown")
def on_shutdown():
    if _worker_stop:
        _worker_stop.set()
    logger.info("Shutdown signal sent")

@app.get("/")
def root():
    with _state_lock:
        return {"service": "ml-service", "status": "ok", "metrics": _latest_metrics}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/config")
def config():
    return {
        "CAMERA_SRC": get_str("CAMERA_SRC", "0"),
        "CAMERA_BACKEND": get_str("CAMERA_BACKEND", "AVFOUNDATION"),
        "STREAM_FPS": get_int("STREAM_FPS", 10),
        "SAMPLE_INTERVAL_S": get_int("SAMPLE_INTERVAL_S", 10),
        "ALERT_THRESHOLD": get_int("ALERT_THRESHOLD", 12),
        "PERSON_SUPPRESS": get_int("PERSON_SUPPRESS", 1),
        "PERSON_AREA_PCT": get_int("PERSON_AREA_PCT", 5),
        "ROI_X": get_int("ROI_X", 0),
        "ROI_Y": get_int("ROI_Y", 0),
        "ROI_W": get_int("ROI_W", 0),
        "ROI_H": get_int("ROI_H", 0),
        "DETECT_COOLDOWN_S": get_int("DETECT_COOLDOWN_S", 300),
        "DETECT_SAVE_DIR": get_str("DETECT_SAVE_DIR", "ml/data/detections"),
        "KNN_ENABLED": get_str("KNN_ENABLED", "true"),
        "KNN_MODEL_PATH": get_str("KNN_MODEL_PATH", "ml/models/knn.joblib"),
        "KNN_NEIGHBORS": get_int("KNN_NEIGHBORS", 5),
    }

def mjpeg_from_latest():
    boundary = b"--frame\r\n"
    while True:
        with _state_lock:
            frame_bytes = _latest_jpeg or _latest_raw_jpeg
            cam = dict(_camera_status)
        if frame_bytes:
            yield (boundary +
                   b"Content-Type: image/jpeg\r\n" +
                   b"Content-Length: " + str(len(frame_bytes)).encode() + b"\r\n\r\n" +
                   frame_bytes + b"\r\n")
        else:
            placeholder = np.zeros((360, 640, 3), dtype=np.uint8)
            msgs = ["Waiting for camera..."]
            if not cam.get("open"):
                msgs.append(f"Not opened (src={cam.get('src')}, backend={cam.get('backend')})")
            if cam.get("last_error"):
                msgs.append(f"Error: {cam.get('last_error')}")
            y = 150
            for m in msgs:
                cv2.putText(placeholder, m, (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
                y += 30
            ok, buf = cv2.imencode(".jpg", placeholder, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            if ok:
                ph = buf.tobytes()
                yield (boundary +
                       b"Content-Type: image/jpeg\r\n" +
                       b"Content-Length: " + str(len(ph)).encode() + b"\r\n\r\n" +
                       ph + b"\r\n")
        time.sleep(0.2)

@app.get("/status")
def status():
    with _state_lock:
        metrics = dict(_latest_metrics)
    st = dict(_camera_status)
    st["saveDetections"] = _save_detections
    return {"camera": st, "metrics": metrics}

@app.post("/camera")
def set_camera(payload: dict):
    src = str(payload.get("src", "0"))
    backend = str(payload.get("backend", "AVFOUNDATION"))
    save_dets = bool(payload.get("saveDetections", False))
    os.environ["CAMERA_SRC"] = src
    os.environ["CAMERA_BACKEND"] = backend
    global _save_detections
    _save_detections = save_dets
    logger.info(f"Set camera requested: src={src}, backend={backend}, saveDetections={save_dets}. Restarting worker.")
    start_worker()
    return {"ok": True, "src": src, "backend": backend, "saveDetections": save_dets}

@app.get("/frame")
def frame():
    with _state_lock:
        frame_bytes = _latest_jpeg or _latest_raw_jpeg
    if not frame_bytes:
        return Response(status_code=204)
    return Response(content=frame_bytes, media_type="image/jpeg")

@app.get("/frame/raw")
def frame_raw():
    with _state_lock:
        frame_bytes = _latest_raw_jpeg
    if not frame_bytes:
        return Response(status_code=204)
    return Response(content=frame_bytes, media_type="image/jpeg")

@app.get("/stream")
def stream():
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Connection": "keep-alive",
    }
    return StreamingResponse(
        mjpeg_from_latest(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers=headers,
    )

@app.get("/stream/html")
def stream_html():
    return HTMLResponse(
        """
        <!doctype html><html><head><meta charset="utf-8"><title>ML Stream</title>
          <style>
            body{margin:0;background:#111;height:100vh;color:#ddd;font-family:system-ui}
            .wrap{display:flex;align-items:center;justify-content:center;height:80vh}
            img{max-width:96vw;max-height:70vh;border:8px solid #333;border-radius:8px;box-shadow:0 10px 30px rgba(0,0,0,.5)}
            .toolbar{display:flex;gap:8px;align-items:center;justify-content:center;padding:10px}
            button{background:#444;color:#fff;border:none;padding:8px 12px;border-radius:6px;cursor:pointer}
            button.primary{background:#0a7}
            button.danger{background:#c33}
            .badge{position:fixed;top:14px;left:14px;background:#222;color:#ddd;padding:6px 10px;border-radius:6px}
            .note{font-size:12px;color:#aaa;text-align:center;margin-top:6px}
          </style>
        </head>
        <body>
          <div class="badge">Stream Kamera</div>
          <div class="wrap"><img id="img" src="/stream" /></div>
          <div class="toolbar">
            <button id="startCam" class="primary">Mulai Kamera</button>
            <span id="dsInfo"></span>
          </div>
          <div class="note">Halaman melihat stream langsung.</div>
          <script>
            const dsInfo = document.getElementById('dsInfo');
            async function refreshStatus(){
              const st = await (await fetch('/status')).json();
              dsInfo.textContent = `Camera open=${st.camera.open} backend=${st.camera.backend || '-'} error=${st.camera.last_error || '-'}`;
            }
            refreshStatus();
            document.getElementById('startCam').onclick = async () => {
              await fetch('/camera', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({src:'0', backend:'AVFOUNDATION'})});
              setTimeout(async () => {
                const st = await (await fetch('/status')).json();
                if (!st.camera.open) {
                  await fetch('/camera', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({src:'0', backend:'ANY'})});
                }
                refreshStatus();
              }, 600);
            };
          </script>
        </body></html>
        """
    )

# Capture-based dataset flow
# Tangkap satu gambar dari kamera (on-demand, tanpa stream)
@app.post("/capture")
def capture(payload: dict = {}):
    global _captured_raw_jpeg
    # Prioritas: jika preview worker aktif, ambil dari buffer live
    with _state_lock:
        live = _latest_raw_jpeg
    if live:
        with _state_lock:
            _captured_raw_jpeg = live
        return {"ok": True, "source": "buffer"}
    # Warm-up capture jika belum ada preview
    src = parse_camera_src()
    backend = str(payload.get("backend", get_str("CAMERA_BACKEND", "AVFOUNDATION")))
    cap = open_capture(src, backend)
    if cap is None:
        return {"ok": False, "error": _camera_status.get("last_error") or "Tidak bisa membuka kamera"}
    try:
        warm_frames = max(10, get_int("CAPTURE_WARM_FRAMES", 15))
        for _ in range(warm_frames):
            ok_w, _ = cap.read()
            if not ok_w:
                break
            time.sleep(0.02)
        ok, frame = cap.read()
    finally:
        try:
            cap.release()
        except Exception:
            pass
    if not ok or frame is None:
        return {"ok": False, "error": "Gagal mengambil gambar dari kamera"}
    ok_raw, raw_jpeg = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    if not ok_raw:
        return {"ok": False, "error": "Gagal meng-encode JPEG"}
    with _state_lock:
        _captured_raw_jpeg = raw_jpeg.tobytes()
    return {"ok": True, "source": "direct"}

@app.get("/capture/image")
def capture_image():
    with _state_lock:
        b = _captured_raw_jpeg
    if not b:
        return Response(status_code=204)
    return Response(content=b, media_type="image/jpeg")

@app.post("/capture/reset")
def capture_reset():
    global _captured_raw_jpeg
    with _state_lock:
        _captured_raw_jpeg = None
    return {"ok": True}

@app.post("/camera/stop")
def camera_stop():
    global _worker_stop
    if _worker_stop:
        _worker_stop.set()
        time.sleep(0.3)
    return {"ok": True}

@app.get("/dataset")
def dataset_html():
    return HTMLResponse(
        """
        <!doctype html><html><head><meta charset="utf-8"><title>Dataset Latih</title>
          <style>
            body{margin:0;background:#111;color:#ddd;font-family:system-ui}
            .wrap{display:flex;align-items:center;justify-content:center;height:72vh}
            img{max-width:96vw;max-height:66vh;border:8px solid #333;border-radius:8px;box-shadow:0 10px 30px rgba(0,0,0,.5)}
            .toolbar{display:flex;gap:10px;align-items:center;justify-content:center;padding:12px;flex-wrap:wrap}
            button{background:#444;color:#fff;border:none;padding:8px 12px;border-radius:6px;cursor:pointer}
            button.primary{background:#0a7}
            button.danger{background:#c33}
            .badge{position:fixed;top:14px;left:14px;background:#222;color:#ddd;padding:6px 10px;border-radius:6px}
            .note{font-size:12px;color:#aaa;text-align:center;margin-top:6px}
            input[type=file]{color:#ddd}
          </style>
        </head>
        <body>
          <div class="badge">Dataset Latih</div>
          <div class="wrap">
            <div id="placeholder" style="width:85vw;height:60vh;background:#000;display:flex;align-items:center;justify-content:center;color:#ddd;border:8px solid #333;border-radius:8px;box-shadow:0 10px 30px rgba(0,0,0,.5)">Belum ada gambar. Tekan Ambil Gambar atau Stay Cam.</div>
            <img id="img" style="display:none" alt="capture" />
          </div>
          <div class="toolbar">
            <button id="btnStayCam">Stay Cam</button>
            <button id="btnStopCam">Stop Cam</button>
            <button id="btnCapture" class="primary">Ambil Gambar</button>
            <button id="btnReset">Reset</button>
            <button id="saveBersih">Simpan BERSIH</button>
            <button id="saveSampah" class="danger">Simpan ADA SAMPAH</button>
            <input type="file" id="uploadFile" accept="image/*" />
            <button id="uploadBersih">Upload BERSIH</button>
            <button id="uploadSampah" class="danger">Upload ADA SAMPAH</button>
            <span id="dsInfo"></span>
          </div>
          <div class="note">Gunakan Stay Cam agar kamera siap (eksposur stabil), lalu Ambil Gambar. Simpan jika sudah sesuai, atau unggah file yang sudah ada.</div>
          <script>
            const dsInfo = document.getElementById('dsInfo');
            const img = document.getElementById('img');
            const placeholder = document.getElementById('placeholder');

            function showImage() {
              img.style.display = '';
              placeholder.style.display = 'none';
            }
            function showPlaceholder() {
              img.style.display = 'none';
              placeholder.style.display = '';
            }

            async function refreshDataset() {
              const s = await (await fetch('/dataset/status')).json();
              const k = await (await fetch('/knn/status')).json();
              dsInfo.textContent = `Dataset: BERSIH=${s.BERSIH} • ADA_SAMPAH=${s.ADA_SAMPAH} • KNN loaded=${k.loaded}`;
            }
            refreshDataset();

            let usingRawFallback = false;
            let rawTimer = null;

            function attachStream() {
              usingRawFallback = false;
              if (rawTimer) { clearInterval(rawTimer); rawTimer = null; }
              img.src = '/stream?ts=' + Date.now();
              showImage();
            }

            function attachRawFallback() {
              if (usingRawFallback) return;
              usingRawFallback = true;
              img.src = '/frame/raw?ts=' + Date.now();
              showImage();
              if (rawTimer) clearInterval(rawTimer);
              rawTimer = setInterval(() => {
                img.src = '/frame/raw?ts=' + Date.now();
              }, 250);
            }

            document.getElementById('btnStayCam').onclick = async () => {
              // Start worker untuk preview (tanpa simpan deteksi)
              await fetch('/camera', {method:'POST', headers:{'Content-Type':'application/json'},
                body: JSON.stringify({src:'0', backend:'AVFOUNDATION', saveDetections:false})});
              await new Promise(r => setTimeout(r, 500));
              // Jika stream gagal, fallback ke snapshot raw
              attachStream();
            };

            document.getElementById('btnStopCam').onclick = async () => {
              await fetch('/camera/stop', {method:'POST'});
              if (rawTimer) { clearInterval(rawTimer); rawTimer = null; }
              showPlaceholder();
            };

            document.getElementById('btnCapture').onclick = async () => {
              // Saat preview aktif, /capture akan mengambil dari buffer live
              let r = await fetch('/capture', {method:'POST', headers:{'Content-Type':'application/json'},
                body: JSON.stringify({backend:'AVFOUNDATION'})});
              let j = await r.json();
              if (!j.ok) {
                r = await fetch('/capture', {method:'POST', headers:{'Content-Type':'application/json'},
                  body: JSON.stringify({backend:'ANY'})});
                j = await r.json();
              }
              if (!j.ok) {
                alert('Gagal ambil gambar: ' + (j.error || 'unknown'));
                return;
              }
              img.src = '/capture/image?ts=' + Date.now();
              showImage();
            };

            document.getElementById('btnReset').onclick = async () => {
              await fetch('/capture/reset', {method:'POST'});
              showPlaceholder();
            };

            async function saveLabel(label) {
              const r = await fetch('/dataset/add', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({label})});
              const j = await r.json();
              alert(j.ok ? `Tersimpan: ${j.path}` : `Gagal: ${j.error || 'unknown'}`);
              refreshDataset();
            }
            document.getElementById('saveBersih').onclick = () => saveLabel('BERSIH');
            document.getElementById('saveSampah').onclick = () => saveLabel('ADA_SAMPAH');

            async function uploadLabel(label) {
              const fileInput = document.getElementById('uploadFile');
              if (!fileInput.files || fileInput.files.length === 0) {
                alert('Pilih file gambar terlebih dahulu.');
                return;
              }
              const file = fileInput.files[0];
              try {
                const r = await fetch('/dataset/upload?label=' + encodeURIComponent(label), {
                  method: 'POST',
                  headers: { 'Content-Type': file.type || 'application/octet-stream' },
                  body: file
                });
                const j = await r.json();
                alert(j.ok ? `Upload berhasil: ${j.file || j.path}` : `Upload gagal: ${j.error || 'unknown'}`);
                refreshDataset();
              } catch (e) {
                alert('Upload error: ' + e);
              }
            }
            document.getElementById('uploadBersih').onclick = () => uploadLabel('BERSIH');
            document.getElementById('uploadSampah').onclick = () => uploadLabel('ADA SAMPAH');
            document.getElementById('uploadFile').addEventListener('change', (e) => {
              const f = e.target.files && e.target.files[0];
              if (f) {
                img.src = URL.createObjectURL(f);
                showImage();
              }
            });
          </script>
        </body></html>
        """
    )

@app.get("/dataset/status")
def dataset_status():
    return dataset_counts()

@app.post("/dataset/add")
def dataset_add(payload: dict = {}):
    label = str(payload.get("label", "")).upper()
    if label not in {"BERSIH", "ADA_SAMPAH"}:
        return {"ok": False, "error": "Label harus BERSIH atau ADA_SAMPAH"}

    with _state_lock:
        raw_bytes = _captured_raw_jpeg
    if not raw_bytes:
        return {"ok": False, "error": "Belum ada gambar yang ditangkap. Tekan Ambil Gambar dulu."}

    out_dir = Path("ml/data/labeled") / label
    ensure_dir(out_dir)
    fname = f"{label.lower()}_{timestamp_str()}.jpg"
    out_path = out_dir / fname
    try:
        with open(out_path, "wb") as f:
            f.write(raw_bytes)
    except Exception as e:
        return {"ok": False, "error": f"Gagal menyimpan: {e}"}

    return {"ok": True, "path": str(out_path), **dataset_counts()}

@app.post("/label")
def label(payload: dict):
    global _captured_raw_jpeg
    ensure_detection_dirs()

    raw_label = str(payload.get("label") or "").strip().upper()
    if raw_label in {"CLEAN", "BERSIH"}:
        label = "BERSIH"
    elif raw_label in {"TRASH", "ADA SAMPAH", "ADA_SAMPAH", "SAMPAH"}:
        label = "ADA SAMPAH"
    else:
        return {"ok": False, "error": "Label harus BERSIH atau ADA SAMPAH"}

    with _state_lock:
        raw_bytes = _captured_raw_jpeg
    if not raw_bytes:
        return {"ok": False, "error": "Belum ada tangkapan. Gunakan /capture untuk ambil gambar."}

    detect_dir = get_detection_dir()
    ensure_dir(detect_dir)
    ts = datetime.utcnow().isoformat(timespec="milliseconds") + "Z"
    short_id = uuid.uuid4().hex[:8]
    safe_label = label.lower().replace(" ", "_")
    fname = f"{ts.replace(':','').replace('.','').replace('-','')}_{safe_label}_{short_id}.jpg"
    out_path = detect_dir / fname

    try:
        with open(out_path, "wb") as f:
            f.write(raw_bytes)
    except Exception as e:
        return {"ok": False, "error": f"Gagal menyimpan: {e}"}

    img = decode_jpeg_to_bgr(raw_bytes)
    if img is None:
        return {"ok": False, "error": "Gagal memuat JPEG untuk ekstraksi fitur."}
    features = extract_features_bgr(img)

    entry = {
        "id": uuid.uuid4().hex,
        "filename": fname,
        "label": label,
        "timestamp": ts,
        "features": features,
    }

    dj = get_dataset_json()
    try:
        with _state_lock:
            data = []
            if dj.exists():
                try:
                    data = json.loads(dj.read_text(encoding="utf-8"))
                    if not isinstance(data, list):
                        data = []
                except Exception:
                    data = []
            data.append(entry)
            dj.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        return {"ok": False, "error": f"Gagal menulis dataset.json: {e}"}

    c = dataset_counts()
    total = c.get("BERSIH", 0) + c.get("ADA_SAMPAH", 0)
    return {"ok": True, "path": str(out_path), "entry": entry, "count": total}

# Dataset utilities

def _count_files(d: Path) -> int:
    if not d.exists():
        return 0
    n = 0
    for p in d.glob("**/*"):
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            n += 1
    return n

def dataset_counts():
    dj = get_dataset_json()
    try:
        if not dj.exists():
            return {"BERSIH": 0, "ADA_SAMPAH": 0, "TOTAL": 0}
        data = json.loads(dj.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            return {"BERSIH": 0, "ADA_SAMPAH": 0, "TOTAL": 0}
        bersih = sum(1 for x in data if str(x.get("label", "")).strip().upper() == "BERSIH")
        sampah = sum(1 for x in data if str(x.get("label", "")).strip().upper() in {"ADA SAMPAH", "ADA_SAMPAH"})
        return {"BERSIH": bersih, "ADA_SAMPAH": sampah, "TOTAL": bersih + sampah}
    except Exception as e:
        logger.error(f"dataset_counts error: {e}")
        return {"BERSIH": 0, "ADA_SAMPAH": 0, "TOTAL": 0}

def dataset_ready() -> bool:
    c = dataset_counts()
    return c.get("TOTAL", c.get("BERSIH", 0) + c.get("ADA_SAMPAH", 0)) > 0

@app.get("/knn/status")
def knn_status():
    return {
        "enabled": get_str("KNN_ENABLED", "true").lower() in {"1","true","yes","y"},
        "loaded": _knn_model is not None,
        "modelPath": get_str("KNN_MODEL_PATH", "ml/models/knn.joblib"),
        "dataset": dataset_counts(),
    }

@app.post("/knn/train")
def knn_train(payload: dict):
    neighbors = int(payload.get("neighbors", get_int("KNN_NEIGHBORS", 5)))
    out_path = Path(payload.get("out", get_str("KNN_MODEL_PATH", "ml/models/knn.joblib")))
    root = Path(payload.get("root", "ml/data/labeled"))

    from .knn import train_knn, load_knn
    counts = dataset_counts()
    if (counts["BERSIH"] + counts["ADA_SAMPAH"]) == 0:
        return {"ok": False, "error": "Dataset kosong. Tambah data latih dulu via /dataset/add atau /dataset"}

    try:
        out = train_knn(labeled_root=root, out_path=out_path, n_neighbors=neighbors)
        model = load_knn(out)
        global _knn_model
        with _state_lock:
            _knn_model = model
        return {
            "ok": True,
            "modelPath": str(out),
            "neighbors": neighbors,
            "dataset": counts
        }
    except Exception as e:
        return {"ok": False, "error": f"Gagal training: {e}"}

@app.post("/knn/reload")
def knn_reload():
    try:
        from .knn import load_knn
        p = Path(get_str("KNN_MODEL_PATH", "ml/models/knn.joblib"))
        if not p.exists():
            return {"ok": False, "error": f"Model tidak ditemukan: {p}"}
        model = load_knn(p)
        global _knn_model
        with _state_lock:
            _knn_model = model
        return {"ok": True, "modelPath": str(p)}
    except Exception as e:
        return {"ok": False, "error": f"Gagal reload: {e}"}

@app.get("/diag/camera")
def diag_camera(src: str | None = None):
    test_src = int(src) if src is not None and src.isdigit() else parse_camera_src()
    results = []
    for name in ["AVFOUNDATION", "ANY", None]:
        label = name or "DEFAULT"
        err = None
        opened = False
        read_ok = False
        try:
            cap = cv2.VideoCapture(test_src, BACKENDS.get(name.upper(), cv2.CAP_ANY)) if name else cv2.VideoCapture(test_src)
            opened = bool(cap and cap.isOpened())
            if opened:
                ok, _ = cap.read()
                read_ok = bool(ok)
            if cap:
                cap.release()
        except Exception as e:
            err = str(e)
        results.append({"backend": label, "opened": opened, "read_ok": read_ok, "error": err})
    return {"src": test_src, "results": results}