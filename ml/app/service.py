# module: service.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, Response, HTMLResponse
import cv2, threading, time, os
from pathlib import Path
from datetime import datetime
import numpy as np

from .config import get_int, get_str
from .utils import get_logger

app = FastAPI()

_latest_jpeg: bytes | None = None
_latest_metrics: dict = {"trashPct": 0.0, "ts": None}
_state_lock = threading.Lock()

# Manajemen worker agar bisa restart saat ganti kamera
_worker_thread: threading.Thread | None = None
_worker_stop: threading.Event | None = None

logger = get_logger("ml-service", Path("ml/logs/ml_service.log"))

# Status kamera untuk diinspeksi dari API
_camera_status: dict = {"open": False, "src": None, "backend": None, "last_error": None}

# Di dekat konstanta BACKENDS
BACKENDS = {
    "ANY": int(cv2.CAP_ANY),
    "AVFOUNDATION": int(cv2.CAP_AVFOUNDATION),  # macOS
}

def parse_camera_src():
    s = get_str("CAMERA_SRC", "0")
    try:
        return int(s)
    except ValueError:
        return s

def open_capture(src, backend_name: str | None):
    tried = []
    def try_backend(name: str):
        b = BACKENDS.get(name.upper(), cv2.CAP_ANY)
        cap = cv2.VideoCapture(src, b)
        tried.append(name)
        if cap.isOpened():
            _camera_status.update({"open": True, "src": src, "backend": name, "last_error": None})
            return cap
        return None

    cap = None
    # coba backend yang diminta
    if backend_name:
        cap = try_backend(backend_name)
    # fallback ke opsi lain
    if cap is None:
        for name in ["AVFOUNDATION", "ANY"]:
            if backend_name and name == backend_name:
                continue
            cap = try_backend(name)
            if cap:
                break

    if cap is None:
        _camera_status.update({"open": False, "src": src, "backend": backend_name, "last_error": f"Failed backends: {tried}"})
    return cap

# Tambahkan classifier wajah global
FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def compute_trash_pct(frame) -> float:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thr = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    fg = cv2.morphologyEx(thr, cv2.MORPH_OPEN, kernel, iterations=1)
    return (float(cv2.countNonZero(fg)) / float(fg.size)) * 100.0

# Tambahan: ROI dan deteksi wajah untuk supresi
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

def camera_worker(stop_event: threading.Event):
    global _latest_jpeg
    src = parse_camera_src()
    backend = get_str("CAMERA_BACKEND", "AVFOUNDATION")
    interval_s = max(1, get_int("SAMPLE_INTERVAL_S", 10))  # minimal jeda antar alert/log
    threshold = get_int("ALERT_THRESHOLD", 12)
    fps = max(1, get_int("STREAM_FPS", 10))  # kecepatan stream MJPEG

    logger.info(f"Camera worker: src={src}, backend={backend}, interval={interval_s}s, threshold={threshold}%")

    cap = open_capture(src, backend)
    if cap is None:
        logger.error(f"Gagal membuka kamera: src={src} backend={backend} | {_camera_status.get('last_error')}")
        return

    # coba set fps (tidak semua backend/driver mendukung)
    cap.set(cv2.CAP_PROP_FPS, fps)

    last_alert_ts = 0.0
    try:
        while not stop_event.is_set():
            ok, frame = cap.read()
            if not ok or frame is None:
                logger.warning("Frame tidak terbaca; retry 0.1s")
                time.sleep(0.1)
                continue

            m = compute_metrics(frame)
            trash_pct = m["trash_pct"]
            suppressed = m["suppressed"]
            rx, ry, rw, rh = m["roi"]

            # Overlay status pada frame
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.0
            thickness = 2
            if suppressed:
                status_text = "Orang terdeteksi — deteksi sampah dinonaktifkan"
                color = (255, 255, 0)
            else:
                status_text = "Ada sampah tertumpuk" if trash_pct >= threshold else "Kondisi normal"
                color = (0, 0, 255) if trash_pct >= threshold else (0, 200, 0)
            text = f"{status_text} • {trash_pct:.2f}%"
            margin = 12
            (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
            cv2.rectangle(frame, (margin - 6, margin - 6), (margin + text_w + 6, margin + text_h + 6), (0, 0, 0), -1)
            cv2.putText(frame, text, (margin, margin + text_h), font, font_scale, color, thickness, cv2.LINE_AA)

            # Gambar ROI bila di-set agar terlihat area yang dievaluasi
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

            # catat alert dengan jeda minimal 'interval_s' agar tidak spam
            now = time.time()
            if not suppressed and trash_pct >= threshold and (now - last_alert_ts) >= interval_s:
                last_alert_ts = now
                logger.info(f"ALERT trashPct={trash_pct:.2f}% (>= {threshold}%)")

            time.sleep(1.0 / fps)
    finally:
        cap.release()
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
    start_worker()
    logger.info("Startup: camera worker started")

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

def mjpeg_from_latest():
    boundary = b"--frame\r\n"
    while True:
        with _state_lock:
            frame_bytes = _latest_jpeg
        if frame_bytes:
            yield (boundary +
                   b"Content-Type: image/jpeg\r\n" +
                   b"Content-Length: " + str(len(frame_bytes)).encode() + b"\r\n\r\n" +
                   frame_bytes + b"\r\n")
        time.sleep(0.2)

@app.get("/status")
def status():
    with _state_lock:
        metrics = dict(_latest_metrics)
    return {"camera": _camera_status, "metrics": metrics}

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

@app.get("/stream.html")
def stream_html():
    return HTMLResponse(
        """
        <!doctype html><html><head><meta charset="utf-8"><title>ML Stream</title>
          <style>
            body{margin:0;background:#111;display:flex;align-items:center;justify-content:center;height:100vh}
            img{max-width:96vw;max-height:92vh;border:8px solid #333;border-radius:8px;box-shadow:0 10px 30px rgba(0,0,0,.5)}
            .badge{position:fixed;top:14px;left:14px;background:#222;color:#ddd;padding:6px 10px;border-radius:6px;font-family:system-ui}
          </style>
        </head>
        <body>
          <div class="badge">Stream Kamera</div>
          <img id="img" src="/stream" />
          <script>
            // Jika koneksi terputus, coba refresh stream otomatis
            const img = document.getElementById('img');
            img.addEventListener('error', () => {
              setTimeout(() => { img.src = '/stream?ts=' + Date.now(); }, 1000);
            });
          </script>
        </body></html>
        """
    )

@app.post("/camera")
def set_camera(payload: dict):
    src = str(payload.get("src", "0"))
    backend = str(payload.get("backend", "AVFOUNDATION"))
    os.environ["CAMERA_SRC"] = src
    os.environ["CAMERA_BACKEND"] = backend
    logger.info(f"Set camera requested: src={src}, backend={backend}. Restarting worker.")
    start_worker()
    return {"ok": True, "src": src, "backend": backend}
@app.get("/frame")
def frame():
    with _state_lock:
        frame_bytes = _latest_jpeg
    if not frame_bytes:
        return Response(status_code=204)
    return Response(content=frame_bytes, media_type="image/jpeg")