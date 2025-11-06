from fastapi import APIRouter
from fastapi.responses import StreamingResponse

stream_router = APIRouter()

@stream_router.get("/stream")
def stream():
    # Lazy import untuk hindari circular import
    from ml.app.service import mjpeg_from_latest
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