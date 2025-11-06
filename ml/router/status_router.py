from fastapi import APIRouter

status_router = APIRouter()

@status_router.get("/status")
def status():
    # Lazy import untuk hindari circular import
    from ml.app.service import _state_lock, _latest_metrics, _camera_status
    with _state_lock:
        metrics = dict(_latest_metrics)
    return {"camera": _camera_status, "metrics": metrics}