from fastapi import FastAPI
from fastapi.responses import Response
import cv2, threading, time,  json
from pathlib import Path
import numpy as np

from .config import get_int, get_str
from .utils import get_logger, ensure_dir
from ml.router.status_router import status_router
from ml.router.stream_router import stream_router
from ml.router.frame_router import frame_router
from ml.router.camera_router import camera_router
from ml.router.dataset_router import dataset_router
from ml.router.knn_router import knn_router
from ml.router.camera_router import camera_router
from ml.router.machine_router import machine_router
from ml.controllers.machine_worker import MachineContext, machine_worker as _machine_worker_controller

# Delegation imports
from ml.app.camera_open import parse_camera_src as _parse_camera_src_impl, open_capture as _open_capture_impl
from ml.app.image_decode import decode_jpeg_to_bgr as _decode_jpeg_to_bgr_impl
from ml.app.image_features import extract_features_bgr as _extract_features_bgr_impl
from ml.app.detection_store import save_detection_and_dataset as _save_detection_and_dataset_impl, get_detection_dir, get_dataset_json, ensure_detection_dirs
from ml.controllers.frame_capture import FrameCaptureContext, get_raw_frame_jpeg as _get_raw_frame_jpeg_controller
from ml.controllers.camera_worker import CameraContext, camera_worker as _camera_worker_controller
from .reference import load_reference_dataset
from .knn import train_knn_from_dataset_json, load_knn

# module: service.py (deklarasi global)
app = FastAPI()
app.include_router(status_router)
app.include_router(stream_router)
app.include_router(frame_router)
app.include_router(camera_router)
app.include_router(dataset_router)
app.include_router(knn_router)
app.include_router(machine_router)


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

# =========================
# Scheduler: Machine Runner
# =========================
_machine_thread: threading.Thread | None = None
_machine_stop: threading.Event | None = None
_machine_status: dict = {
    "running": False,
    "last_run": None,
    "run_count": 0,
    "interval_min": None,
    "last_result": None,
}

def get_machine_interval_min() -> int:
    return max(1, get_int("MACHINE_INTERVAL_MINUTES", 5))

def _get_raw_frame_jpeg() -> bytes | None:
    ctx = FrameCaptureContext(
        state_lock=_state_lock,
        latest_raw_jpeg_getter=lambda: _latest_raw_jpeg,
        get_int=get_int,
        get_str=get_str,
        logger=logger,
        camera_status_ref=_camera_status,
    )
    return _get_raw_frame_jpeg_controller(ctx)

def _save_detection_and_dataset(raw_bytes: bytes, label_norm: str, knn_conf: float | None, trash_pct: float, roi: tuple[int,int,int,int]) -> dict:
    return _save_detection_and_dataset_impl(raw_bytes, label_norm, knn_conf, trash_pct, roi, logger)

def machine_worker(stop_event: threading.Event):
    ctx = MachineContext(
        state_lock=_state_lock,
        machine_status=_machine_status,
        get_int=get_int,
        get_str=get_str,
        get_raw_frame_jpeg=_get_raw_frame_jpeg,
        save_detection_and_dataset=_save_detection_and_dataset,
        decode_jpeg_to_bgr=decode_jpeg_to_bgr,
        compute_metrics=compute_metrics,
        knn_model_getter=lambda: _knn_model,
        logger=logger,
    )
    return _machine_worker_controller(stop_event, ctx)

def start_machine():
    global _machine_thread, _machine_stop
    if _machine_stop:
        _machine_stop.set()
        time.sleep(0.5)
    _machine_stop = threading.Event()
    _machine_thread = threading.Thread(target=machine_worker, args=(_machine_stop,), daemon=True)
    _machine_thread.start()
    return True

def stop_machine():
    global _machine_stop
    if _machine_stop:
        _machine_stop.set()
        time.sleep(0.3)
    return True

def get_machine_status() -> dict:
    with _state_lock:
        return dict(_machine_status)

_camera_status: dict = {"open": False, "src": None, "backend": None, "last_error": None}

BACKENDS = {
    "ANY": int(cv2.CAP_ANY),
    "AVFOUNDATION": int(cv2.CAP_AVFOUNDATION),  # macOS
}

FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def parse_camera_src():
    return _parse_camera_src_impl()

def open_capture(src, backend_name: str | None):
    return _open_capture_impl(src, backend_name, _camera_status, logger)

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
    # Simpan dataset.json di root data, bukan di dalam detections
    return Path("ml/data/dataset.json")

def ensure_detection_dirs():
    try:
        # Pastikan folder untuk gambar deteksi ada
        detect_dir = get_detection_dir()
        ensure_dir(detect_dir)

        # Pastikan root data ada
        data_root = Path("ml/data")
        ensure_dir(data_root)

        # Inisialisasi dataset.json di lokasi baru
        dj = get_dataset_json()
        if not dj.exists():
            # Migrasi otomatis dari lokasi lama jika ada
            old_dj = detect_dir / "dataset.json"
            if old_dj.exists():
                try:
                    items = json.loads(old_dj.read_text(encoding="utf-8") or "[]")
                    dj.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
                except Exception as mig_err:
                    logger.warning(f"Gagal migrasi dataset.json lama: {mig_err}")
                    dj.write_text("[]", encoding="utf-8")
            else:
                dj.write_text("[]", encoding="utf-8")
    except Exception as e:
        logger.error(f"ensure_detection_dirs error: {e}")


def decode_jpeg_to_bgr(jpeg_bytes: bytes):
    return _decode_jpeg_to_bgr_impl(jpeg_bytes)


def extract_features_bgr(img):
    return _extract_features_bgr_impl(img)

def camera_worker(stop_event: threading.Event):
    def _set_latest_jpeg(b: bytes | None):
        global _latest_jpeg
        with _state_lock:
            _latest_jpeg = b

    def _set_latest_raw_jpeg(b: bytes | None):
        global _latest_raw_jpeg
        with _state_lock:
            _latest_raw_jpeg = b

    def _update_metrics(d: dict):
        with _state_lock:
            _latest_metrics.update(d)

    ctx = CameraContext(
        state_lock=_state_lock,
        camera_status=_camera_status,
        set_latest_jpeg=_set_latest_jpeg,
        set_latest_raw_jpeg=_set_latest_raw_jpeg,
        update_metrics=_update_metrics,
        save_detections_getter=lambda: _save_detections,
        knn_model_getter=lambda: _knn_model,
        logger=logger,
    )
    return _camera_worker_controller(stop_event, ctx)

def start_worker():
    global _worker_thread, _worker_stop
    if _worker_stop:
        _worker_stop.set()
        time.sleep(0.5)
    _worker_stop = threading.Event()
    _worker_thread = threading.Thread(target=camera_worker, args=(_worker_stop,), daemon=True)
    _worker_thread.start()

def stop_worker():
    global _worker_stop
    if _worker_stop:
        _worker_stop.set()
        time.sleep(0.3)
    return True

@app.on_event("startup")
def on_startup():
    # Pastikan deklarasi global muncul sebelum assignment apa pun di fungsi ini
    global _knn_model

    logger.info("Startup: kamera tidak dibuka otomatis. Gunakan tombol Mulai Kamera.")
    try:
        if get_str("KNN_ENABLED", "true").lower() in {"1","true","yes","y"}:
            p = Path(get_str("KNN_MODEL_PATH", "ml/models/knn.joblib"))
            # Cek dataset; hanya load model jika dataset siap dan file model ada
            counts = dataset_counts()
            total = counts.get("TOTAL", counts.get("BERSIH", 0) + counts.get("ADA_SAMPAH", 0) + counts.get("SAMPAH_MENUMPUK", 0))
            if total > 0 and p.exists():
                from .knn import load_knn
                _knn_model = load_knn(p)
                logger.info(f"Startup: KNN model loaded {p} (dataset total={total})")
            else:
                _knn_model = None
                logger.info(f"Startup: KNN not loaded (dataset total={total}, model exists={p.exists()})")
        # Muat dataset referensi untuk similarity
        ref = load_reference_dataset(Path("ml/data/dataset.json"))
        logger.info(f"Startup: reference dataset load status={ref.get('ok')} count={ref.get('count')}")
    except Exception as e:
        logger.error(f"Startup: gagal memuat KNN/Reference: {e}")

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

# MJPEG generator (digunakan oleh stream_router)
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

# Capture-based dataset flow (tetap di service)
@app.post("/camera")
def set_camera(payload: dict):
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

@app.post("/camera/stop")
def camera_stop():
    return dataset_counts()

@app.post("/capture/reset")
def capture_reset():
    global _captured_raw_jpeg
    with _state_lock:
        _captured_raw_jpeg = None
    return {"ok": True}


def dataset_counts():
    dj = get_dataset_json()
    try:
        if not dj.exists():
            return {"BERSIH": 0, "ADA_SAMPAH": 0, "SAMPAH_MENUMPUK": 0, "TOTAL": 0}
        data = json.loads(dj.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            return {"BERSIH": 0, "ADA_SAMPAH": 0, "SAMPAH_MENUMPUK": 0, "TOTAL": 0}
        bersih = sum(1 for x in data if str(x.get("label", "")).strip().upper() == "BERSIH")
        ada = sum(1 for x in data if str(x.get("label", "")).strip().upper() in {"ADA SAMPAH", "ADA_SAMPAH"})
        menumpuk = sum(1 for x in data if str(x.get("label", "")).strip().upper() in {"SAMPAH MENUMPUK", "SAMPAH_MENUMPUK"})
        return {"BERSIH": bersih, "ADA_SAMPAH": ada, "SAMPAH_MENUMPUK": menumpuk, "TOTAL": bersih + ada + menumpuk}
    except Exception as e:
        logger.error(f"dataset_counts error: {e}")
        return {"BERSIH": 0, "ADA_SAMPAH": 0, "SAMPAH_MENUMPUK": 0, "TOTAL": 0}

def dataset_ready() -> bool:
    c = dataset_counts()
    return c.get("TOTAL", c.get("BERSIH", 0) + c.get("ADA_SAMPAH", 0) + c.get("SAMPAH_MENUMPUK", 0)) > 0
