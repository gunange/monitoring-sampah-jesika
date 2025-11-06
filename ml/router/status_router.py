from fastapi import APIRouter

status_router = APIRouter()

@status_router.get("/status")
def status():
    # Lazy import untuk hindari circular import
    from ml.app.service import _state_lock, _latest_metrics, _camera_status
    with _state_lock:
        metrics = dict(_latest_metrics)
    return {"camera": _camera_status, "metrics": metrics}

@status_router.get("/config")
def config():
    # Lazy import untuk hindari circular import
    from ml.app.config import get_int, get_str
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