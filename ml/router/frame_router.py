from fastapi import APIRouter, Response
from ml.app.service import _state_lock, _latest_jpeg, _latest_raw_jpeg

frame_router = APIRouter()

@frame_router.get("/frame")
def frame():
    with _state_lock:
        frame_bytes = _latest_jpeg
    if not frame_bytes:
        return Response(status_code=204)
    return Response(content=frame_bytes, media_type="image/jpeg")

@frame_router.get("/frame/raw")
def frame_raw():
    with _state_lock:
        frame_bytes = _latest_raw_jpeg
    if not frame_bytes:
        return Response(status_code=204)
    return Response(content=frame_bytes, media_type="image/jpeg")