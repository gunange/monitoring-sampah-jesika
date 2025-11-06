from fastapi import APIRouter
from ml.app.service import _state_lock, _latest_metrics, _camera_status

status_router = APIRouter()

@status_router.get("/status")
def status():
    with _state_lock:
        metrics = dict(_latest_metrics)
    return {"camera": _camera_status, "metrics": metrics}