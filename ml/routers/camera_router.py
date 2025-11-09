from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from ml.app.services import logger, camera_service

camera_router = APIRouter()

@camera_router.get("/camera")
def camera_status():
    
    return camera_service.get_status()

@camera_router.get("/camera/list")
def camera_list():
    from ml.app.config import get_int, get_str
    from ml.app.camera import open_capture

    backend = get_str("CAMERA_BACKEND", "AVFOUNDATION")
    max_scan = max(1, get_int("CAMERA_SCAN_MAX", 5))  # default scan 5 indeks
    cameras = []
    for idx in range(max_scan):
        status = {}
        cap = open_capture(idx, backend, status, logger)
        if cap:
            try:
                cap.release()
            except Exception:
                pass
        cameras.append({
            "index": idx,
            "available": bool(status.get("open")),
            "backend": status.get("backend") or backend,
            "last_error": status.get("last_error"),
        })
    return {"backend": backend, "count": len(cameras), "cameras": cameras}

@camera_router.get("/camera/start")
def camera_start():

    ok =  camera_service.start()
    return {"started": ok, "status": camera_service.get_status()}

@camera_router.get("/camera/stop")
def camera_stop():
    
    camera_service.stop()
    return {"stopped": True, "status": camera_service.get_status()}

@camera_router.get("/camera/stream")
def stream():
    # Lazy import untuk hindari circular import dan akses state terpusat
    from fastapi import HTTPException
    from ml.app.config import get_int
    import cv2, time

    cap = camera_service.get_cap()
    if cap is None:
        camera_service.start()
        cap = camera_service.get_cap()
        if camera_service.get_cap() is None:
            status = camera_service.get_status()
            raise HTTPException(status_code=409, detail=f"Camera gagal start: {status.get('last_error')}")

    fps = max(1, get_int("STREAM_FPS", 10))
    boundary = b"--frame\r\n"
    def gen():
        try:
            while True:
                ok, frame = cap.read()
                if not ok or frame is None:
                    break
                # kirim frame original tanpa resize
                ok2, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
                if not ok2:
                    continue
                b = buf.tobytes()
                yield (boundary +
                       b"Content-Type: image/jpeg\r\n" +
                       b"Content-Length: " + str(len(b)).encode() + b"\r\n\r\n" +
                       b + b"\r\n")
                time.sleep(1.0 / float(fps))
        finally:
            try:
                cap.release()
            except Exception:
                pass
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Connection": "keep-alive",
    }
    return StreamingResponse(
        gen(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers=headers,
    )