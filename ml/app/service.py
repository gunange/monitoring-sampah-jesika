# module: service.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, Response, HTMLResponse
import cv2, threading, time, os, json
from pathlib import Path
from datetime import datetime
import numpy as np

from .config import get_int, get_str
from .utils import get_logger, ensure_dir, timestamp_str

# module: service.py (deklarasi global)
# Di bagian atas import, tambahkan import router berikut:
from ..router.frame_router import frame_router
from ..router.dataset_router import dataset_router
from ..router.status_router import status_router
from ..router.stream_router import stream_router
from ..router.camera_router import camera_router
from ..router.knn_router import knn_router
# module: service.py (set up app dan router)
app = FastAPI()

_latest_jpeg: bytes | None = None
_latest_raw_jpeg: bytes | None = None
_latest_metrics: dict = {"trashPct": 0.0, "ts": None}
_state_lock = threading.Lock()

# Model KNN global (dipakai oleh worker dan route training)
_knn_model = None

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
    global _knn_model
    src = parse_camera_src()
    backend = get_str("CAMERA_BACKEND", "AVFOUNDATION")
    interval_s = max(1, get_int("SAMPLE_INTERVAL_S", 10))
    threshold = get_int("ALERT_THRESHOLD", 12)
    fps = max(1, get_int("STREAM_FPS", 10))

    # Inisialisasi variabel cooldown dan direktori simpan deteksi
    detect_cooldown_s = max(1, get_int("DETECT_COOLDOWN_S", 300))
    detect_save_dir = get_str("DETECT_SAVE_DIR", "ml/data/detections")

    # KNN: jika diaktifkan dan belum ada di memori, coba load dari path
    knn_enabled = get_str("KNN_ENABLED", "true").lower() in {"1", "true", "yes", "y"}
    knn_model_path = get_str("KNN_MODEL_PATH", "ml/models/knn.joblib")
    if knn_enabled and _knn_model is None and Path(knn_model_path).exists():
        try:
            from .knn import load_knn
            _knn_model = load_knn(Path(knn_model_path))
            logger.info(f"KNN model loaded in worker: {knn_model_path}")
        except Exception as e:
            logger.error(f"Gagal memuat KNN di worker: {e}")
    detections_json = get_str("DETECTIONS_JSON", "ml/logs/detections.json")

    # Buka kamera (retry loop)
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

    # coba set fps (tidak semua backend/driver mendukung)
    cap.set(cv2.CAP_PROP_FPS, fps)

    # Inisialisasi counter gagal baca frame
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
                if fail_count >= 30:  # ~3 detik gagal baca, coba re-open
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

            # Simpan frame mentah (tanpa overlay) untuk labeling
            raw_frame = frame.copy()
            ok_raw, raw_jpeg = cv2.imencode(".jpg", raw_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
            if ok_raw:
                with _state_lock:
                    _latest_raw_jpeg = raw_jpeg.tobytes()

            m = compute_metrics(frame)
            trash_pct = m["trash_pct"]
            suppressed = m["suppressed"]
            rx, ry, rw, rh = m["roi"]

            # Inferensi KNN jika tersedia
            knn_label, knn_conf = None, None
            if _knn_model is not None and not suppressed:
                try:
                    roi_img = raw_frame[ry:ry+rh, rx:rx+rw] if rw > 0 and rh > 0 else raw_frame
                    from .knn import predict_knn
                    knn_label, knn_conf = predict_knn(_knn_model, roi_img)
                except Exception as e:
                    logger.error(f"KNN infer error: {e}")

            # Keputusan akhir berdasarkan KNN bila tersedia
            is_trash = False
            if suppressed:
                is_trash = False
            elif knn_label is not None:
                is_trash = (knn_label == "ADA_SAMPAH")
            else:
                # fallback: heuristik trash_pct
                is_trash = trash_pct >= threshold

            # Overlay status pada frame
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.0
            thickness = 2
            if suppressed:
                status_text = "Orang terdeteksi — deteksi sampah dinonaktifkan"
                color = (255, 255, 0)
            else:
                # Tampilkan label KNN jika ada
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

            # Simpan event deteksi ke JSON (list objek)
            now = time.time()
            can_capture = (now - last_capture_ts) >= detect_cooldown_s
            if is_trash and not suppressed and can_capture:
                ensure_dir(Path(detect_save_dir))
                out_path = Path(detect_save_dir) / f"trash_{timestamp_str()}.jpg"
                ok_save = cv2.imwrite(str(out_path), raw_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
                if ok_save:
                    last_capture_ts = now

                try:
                    ensure_dir(Path(detections_json).parent)
                    import json
                    event = {
                        "ts": datetime.now().isoformat(),
                        "label": knn_label if knn_label is not None else ("ADA_SAMPAH" if is_trash else "BERSIH"),
                        "knnConfidence": knn_conf,
                        "trashPct": round(trash_pct, 2),
                        "suppressed": suppressed,
                        "roi": {"x": rx, "y": ry, "w": rw, "h": rh},
                        "imagePath": str(out_path) if ok_save else None,
                    }
                    # Append sebagai list JSON
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

            # (Opsional) log overlay dengan jeda minimal
            if is_trash and not suppressed and (now - last_alert_ts) >= interval_s:
                last_alert_ts = now

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
    # Jangan auto-start kamera bila dataset kosong; nyalakan manual via /camera atau dataset
    if dataset_ready():
        start_worker()
        logger.info("Startup: dataset tersedia, kamera dibuka.")
    else:
        logger.info("Startup: dataset kosong, kamera tidak dibuka.")

    # Muat KNN jika diaktifkan dan file model tersedia
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
        "DETECTIONS_JSON": get_str("DETECTIONS_JSON", "ml/logs/detections.json"),
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
            frame_bytes = _latest_jpeg
            cam = dict(_camera_status)
        if frame_bytes:
            yield (boundary +
                   b"Content-Type: image/jpeg\r\n" +
                   b"Content-Length: " + str(len(frame_bytes)).encode() + b"\r\n\r\n" +
                   frame_bytes + b"\r\n")
        else:
            # Fallback: tampilkan status kamera agar user paham kenapa belum tampil
            placeholder = np.zeros((360, 640, 3), dtype=np.uint8)
            msgs = ["Waiting for camera..."]
            if not cam.get("open"):
                msgs.append(f"Not opened (src={cam.get('src')}, backend={cam.get('backend')})")
            if cam.get("last_error"):
                msgs.append(f"Error: {cam.get('last_error')}")
            y = 150
            for m in msgs:
                cv2.putText(placeholder, m, (20, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
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

@app.get("/stream")
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
            <button id="saveBersih">Simpan BERSIH</button>
            <button id="saveSampah" class="danger">Simpan ADA SAMPAH</button>
            <span id="dsInfo"></span>
          </div>
          <div class="note">Gunakan tombol untuk membuat data latih. Kamera tidak otomatis dibuka saat dataset kosong.</div>
          <script>
            const dsInfo = document.getElementById('dsInfo');
            async function refreshDataset() {
              const r = await fetch('/dataset/status');
              const j = await r.json();
              dsInfo.textContent = `Dataset: BERSIH=${j.BERSIH} • ADA_SAMPAH=${j.ADA_SAMPAH}`;
            }
            refreshDataset();

            const img = document.getElementById('img');
            let rawFallbackTimer = null;

            async function useRawFallback() {
              if (rawFallbackTimer) return;
              rawFallbackTimer = setInterval(() => {
                img.src = '/frame/raw?ts=' + Date.now();
              }, 1000);
            }

            img.addEventListener('error', () => {
              setTimeout(() => { img.src = '/stream?ts=' + Date.now(); }, 500);
              setTimeout(useRawFallback, 1500);
            });

            document.getElementById('startCam').onclick = async () => {
              // Coba AVFOUNDATION dulu
              await fetch('/camera', {method:'POST', headers:{'Content-Type':'application/json'},
                body: JSON.stringify({src:'0', backend:'AVFOUNDATION'})});
              // Jika belum terbuka, fallback ke ANY
              setTimeout(async () => {
                const st = await (await fetch('/status')).json();
                if (!st.camera.open) {
                  await fetch('/camera', {method:'POST', headers:{'Content-Type':'application/json'},
                    body: JSON.stringify({src:'0', backend:'ANY'})});
                }
                refreshDataset();
              }, 600);
            };

            async function saveLabel(label) {
              const r = await fetch('/label', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({label})});
              const j = await r.json();
              alert(j.ok ? `Tersimpan: ${j.path}` : `Gagal: ${j.error || 'unknown'}`);
              refreshDataset();
            }
            document.getElementById('saveBersih').onclick = () => saveLabel('BERSIH');
            document.getElementById('saveSampah').onclick = () => saveLabel('ADA_SAMPAH');
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

# module: service.py (routes frame/raw, dataset/status, dataset/add)
@app.get("/frame/raw")
def frame_raw():
    with _state_lock:
        frame_bytes = _latest_raw_jpeg
    if not frame_bytes:
        return Response(status_code=204)
    return Response(content=frame_bytes, media_type="image/jpeg")

@app.get("/dataset")
def dataset_html():
    return HTMLResponse(
        """
        <!doctype html><html><head><meta charset="utf-8"><title>Dataset Latih</title>
          <style>
            body{margin:0;background:#111;color:#ddd;font-family:system-ui}
            .wrap{display:flex;align-items:center;justify-content:center;height:72vh}
            img{max-width:96vw;max-height:66vh;border:8px solid #333;border-radius:8px;box-shadow:0 10px 30px rgba(0,0,0,.5)}
            .toolbar{display:flex;gap:10px;align-items:center;justify-content:center;padding:12px}
            button{background:#444;color:#fff;border:none;padding:8px 12px;border-radius:6px;cursor:pointer}
            button.primary{background:#0a7}
            button.danger{background:#c33}
            .badge{position:fixed;top:14px;left:14px;background:#222;color:#ddd;padding:6px 10px;border-radius:6px}
            .note{font-size:12px;color:#aaa;text-align:center;margin-top:6px}
          </style>
        </head>
        <body>
          <div class="badge">Dataset Latih</div>
          <div class="wrap"><img id="img" src="/stream" /></div>
          <div class="toolbar">
            <button id="startCam" class="primary">Mulai Kamera</button>
            <button id="saveBersih">Simpan BERSIH</button>
            <button id="saveSampah" class="danger">Simpan ADA SAMPAH</button>
            <button id="trainKNN">Latih KNN (k=5)</button>
            <span id="dsInfo"></span>
          </div>
          <div class="note">Kamera perlu dinyalakan manual. Setelah cukup sampel, latih KNN.</div>
          <script>
            const dsInfo = document.getElementById('dsInfo');
            const img = document.getElementById('img');

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
            }

            function attachRawFallback() {
              if (usingRawFallback) return;
              usingRawFallback = true;
              img.src = '/frame/raw?ts=' + Date.now();
              if (rawTimer) clearInterval(rawTimer);
              rawTimer = setInterval(() => {
                img.src = '/frame/raw?ts=' + Date.now();
              }, 1000);
            }

            img.addEventListener('error', () => {
              // Jika stream MJPEG error, pakai fallback snapshot raw yang refresh tiap detik
              attachRawFallback();
            });

            async function tryStartCamera() {
              // Coba AVFOUNDATION terlebih dahulu
              await fetch('/camera', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({src:'0', backend:'AVFOUNDATION'})});
              await new Promise(r => setTimeout(r, 400));

              const st = await (await fetch('/status')).json();
              if (!st.camera || st.camera.open !== true) {
                // Ganti ke ANY jika belum terbuka
                await fetch('/camera', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({src:'0', backend:'ANY'})});
                await new Promise(r => setTimeout(r, 600));
              }

              const st2 = await (await fetch('/status')).json();
              if (st2.camera && st2.camera.open === true) {
                // Pasang stream MJPEG; jika gagal, listener di atas akan fallback ke raw
                attachStream();
              } else {
                // Tetap gunakan fallback raw jika kamera belum ready
                attachRawFallback();
              }

              refreshDataset();
            }

            document.getElementById('startCam').onclick = async () => {
              await tryStartCamera();
            };

            async function saveLabel(label) {
              const r = await fetch('/dataset/add', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({label})});
              const j = await r.json();
              alert(j.ok ? `Tersimpan: ${j.path}` : `Gagal: ${j.error || 'unknown'}`);
              refreshDataset();
            }
            document.getElementById('saveBersih').onclick = () => saveLabel('BERSIH');
            document.getElementById('saveSampah').onclick = () => saveLabel('ADA_SAMPAH');

            document.getElementById('trainKNN').onclick = async () => {
              const r = await fetch('/knn/train', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({neighbors:5})});
              const j = await r.json();
              alert(j.ok ? `Model: ${j.modelPath}` : `Training gagal: ${j.error || 'unknown'}`);
              refreshDataset();
            };
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

# module: service.py (routes frame/raw, dataset/status, dataset/add)
@app.get("/frame/raw")
def frame_raw():
    with _state_lock:
        frame_bytes = _latest_raw_jpeg
    if not frame_bytes:
        return Response(status_code=204)
    return Response(content=frame_bytes, media_type="image/jpeg")

@app.get("/dataset/status")
def dataset_status():
    # new code:
    return dataset_counts()

@app.post("/dataset/add")
def dataset_add(payload: dict):
    # new code:
    label = str(payload.get("label", "")).upper()
    if label not in {"BERSIH", "ADA_SAMPAH"}:
        return {"ok": False, "error": "Label harus BERSIH atau ADA_SAMPAH"}

    with _state_lock:
        raw_bytes = _latest_raw_jpeg
    if not raw_bytes:
        return {"ok": False, "error": "Belum ada frame mentah. Nyalakan kamera dan tunggu frame."}

    out_dir = Path("ml/data/labeled") / label
    ensure_dir(out_dir)
    fname = f"{label.lower()}_{timestamp_str()}.jpg"
    out_path = out_dir / fname
    try:
        with open(out_path, "wb") as f:
            f.write(raw_bytes)
    except Exception as e:
        return {"ok": False, "error": f"Gagal menyimpan: {e}"}

    counts = dataset_counts()
    return {"ok": True, "path": str(out_path), **counts}

@app.post("/label")
def label(payload: dict):
    label = str(payload.get("label", "")).upper()
    if label not in {"BERSIH", "ADA_SAMPAH"}:
        return {"ok": False, "error": "Label harus BERSIH atau ADA_SAMPAH"}

    with _state_lock:
        raw_bytes = _latest_raw_jpeg
    if not raw_bytes:
        return {"ok": False, "error": "Belum ada frame mentah. Mulai kamera terlebih dahulu."}

    ensure_dir(Path("ml/data/labeled") / label)
    fname = f"{label.lower()}_{timestamp_str()}.jpg"
    out_path = Path("ml/data/labeled") / label / fname
    try:
        with open(out_path, "wb") as f:
            f.write(raw_bytes)
    except Exception as e:
        return {"ok": False, "error": f"Gagal menyimpan: {e}"}

    # Jika dataset baru tersedia dan worker belum jalan, buka kamera
    if not dataset_ready():
        # setelah menyimpan satu, dataset_ready() bisa true — cek lagi
        pass
    if dataset_ready() and (_worker_thread is None or not _worker_thread.is_alive()):
        start_worker()

    c = dataset_counts()
    return {"ok": True, "path": str(out_path), **c}

# Util dataset latih
# module: service.py (util dataset latih)
def _count_files(d: Path) -> int:
    # new code:
    if not d.exists():
        return 0
    n = 0
    for p in d.glob("**/*"):
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            n += 1
    return n

def dataset_counts():
    root = Path("ml/data/labeled")
    return {
        "BERSIH": _count_files(root / "BERSIH"),
        "ADA_SAMPAH": _count_files(root / "ADA_SAMPAH"),
    }

def dataset_ready() -> bool:
    c = dataset_counts()
    return (c["BERSIH"] + c["ADA_SAMPAH"]) > 0

@app.get("/knn/status")
def knn_status():
    # new code:
    return {
        "enabled": get_str("KNN_ENABLED", "true").lower() in {"1","true","yes","y"},
        "loaded": _knn_model is not None,
        "modelPath": get_str("KNN_MODEL_PATH", "ml/models/knn.joblib"),
        "dataset": dataset_counts(),
    }

@app.post("/knn/train")
def knn_train(payload: dict):
    # Latih KNN dari folder ml/data/labeled, muat ke memori, dan kembalikan ringkasan
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