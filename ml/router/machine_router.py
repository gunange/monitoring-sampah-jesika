from fastapi import APIRouter
from pathlib import Path

machine_router = APIRouter()

@machine_router.get("/machine/status")
def machine_status():
    # Lazy import untuk hindari circular import
    from ml.app import service as svc
    from ml.app.config import get_int, get_str
    counts = svc.dataset_counts()
    status = svc.get_machine_status()
    with svc._state_lock:
        knn_loaded = svc._knn_model is not None
    return {
        "machine": {
            **status,
            "intervalMin": int(svc.get_machine_interval_min()),
        },
        "dataset": {
            "TOTAL": counts.get("TOTAL", counts.get("BERSIH", 0) + counts.get("ADA_SAMPAH", 0) + counts.get("SAMPAH_MENUMPUK", 0)),
            "BERSIH": counts.get("BERSIH", 0),
            "ADA_SAMPAH": counts.get("ADA_SAMPAH", 0),
            "SAMPAH_MENUMPUK": counts.get("SAMPAH_MENUMPUK", 0),
        },
        "knn": {
            "enabled": get_str("KNN_ENABLED", "true"),
            "neighbors": get_int("KNN_NEIGHBORS", 5),
            "modelPath": get_str("KNN_MODEL_PATH", "ml/models/knn.joblib"),
            "loaded": knn_loaded,
        },
        "cameraConfig": {
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
        },
    }

@machine_router.get("/machine/start")
def machine_start():
    # Lazy import untuk hindari circular import
    from ml.app import service as svc
    # Pastikan direktori deteksi siap
    svc.ensure_detection_dirs()
    # Nyalakan kamera worker (preview/stream buffer) agar kamera tetap ON
    svc.start_worker()
    # Nyalakan scheduler machine (pekerja berkala)
    svc.start_machine()
    return {"ok": True, "status": svc.get_machine_status()}

@machine_router.get("/machine/stop")
def machine_stop():
    # Lazy import untuk hindari circular import
    from ml.app import service as svc
    # Hentikan scheduler terlebih dahulu
    svc.stop_machine()
    # Lalu matikan kamera worker
    svc.stop_worker()
    return {"ok": True, "status": svc.get_machine_status()}

@machine_router.get("/machine/reload")
def machine_reload():
    # Reload env dan model KNN (jika dataset siap dan file model ada)
    from ml.app.config import load_env, get_str
    from ml.app.knn import load_knn
    from ml.app import service as svc

    # Muat .env kembali
    load_env(Path(__file__).resolve().parents[1] / ".env")

    # Restart kamera worker agar konfigurasi baru (mis. ROI, FPS, backend) efektif
    try:
        svc.stop_worker()
        svc.start_worker()
    except Exception:
        pass

    # Reload KNN jika siap
    try:
        p = Path(get_str("KNN_MODEL_PATH", "ml/models/knn.joblib"))
        if svc.dataset_ready() and p.exists():
            model = load_knn(p)
            with svc._state_lock:
                svc._knn_model = model
            knn_status = {"reloaded": True, "modelPath": str(p)}
        else:
            knn_status = {"reloaded": False, "reason": "dataset_not_ready_or_model_missing", "modelPath": str(p)}
    except Exception as e:
        knn_status = {"reloaded": False, "error": str(e)}

    return {"ok": True, "knn": knn_status}