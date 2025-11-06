from fastapi import APIRouter, Response

frame_router = APIRouter()

@frame_router.get("/frame")
def frame():
    # Lazy import untuk hindari circular import
    from ml.app.service import _state_lock, _latest_jpeg
    with _state_lock:
        frame_bytes = _latest_jpeg
    if not frame_bytes:
        return Response(status_code=204)
    return Response(content=frame_bytes, media_type="image/jpeg")

@frame_router.get("/frame/raw")
def frame_raw():
    # Lazy import untuk hindari circular import
    from ml.app.service import _state_lock, _latest_raw_jpeg
    with _state_lock:
        frame_bytes = _latest_raw_jpeg
    if not frame_bytes:
        return Response(status_code=204)
    return Response(content=frame_bytes, media_type="image/jpeg")