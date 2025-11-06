import os
from fastapi import APIRouter
from ml.app.service import start_worker, logger

camera_router = APIRouter()

@camera_router.post("/camera")
def set_camera(payload: dict):
    src = str(payload.get("src", "0"))
    backend = str(payload.get("backend", "AVFOUNDATION"))
    os.environ["CAMERA_SRC"] = src
    os.environ["CAMERA_BACKEND"] = backend
    logger.info(f"Set camera requested: src={src}, backend={backend}. Restarting worker.")
    start_worker()
    return {"ok": True, "src": src, "backend": backend}