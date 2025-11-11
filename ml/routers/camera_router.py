# function stream() and last_frame()
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from ml.services.main_service import camera_controller

camera_router = APIRouter()

@camera_router.get("/camera")
def camera_status():
    
    return camera_controller.get_status()

@camera_router.get("/camera/list")
def camera_list():
    from ml.app.config import get_int, get_str
    from ml.app.camera import open_capture

    backend = get_str("CAMERA_BACKEND", "AVFOUNDATION")
    max_scan = max(1, get_int("CAMERA_SCAN_MAX", 5))  # default scan 5 indeks
    cameras = []
    for idx in range(max_scan):
        status = {}
        cap = open_capture(idx, backend, status)
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

    ok =  camera_controller.start()
    return {"started": ok, "status": camera_controller.get_status()}

@camera_router.get("/camera/stop")
def camera_stop():
    
    camera_controller.stop()
    return {"stopped": True, "status": camera_controller.get_status()}

@camera_router.get("/camera/stream")
def stream():
    # Lazy import untuk hindari circular import dan akses state terpusat
    from fastapi import HTTPException
    from ml.app.config import get_int
    import cv2, time

    cap = camera_controller.get_cap()
    if cap is None:
        status = camera_controller.get_status()
        raise HTTPException(status_code=404, detail=f"Camera belum siap: {status.get('last_error')}")

    fps = max(1, get_int("STREAM_FPS", 10))
    boundary = b"--frame\r\n"
    def gen():
        try:
            while True:
                ok, frame = camera_controller.read_frame()
                if not ok or frame is None:
                    break
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
            # Lifecycle kamera dikelola oleh camera_controller
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

@camera_router.get("/camera/last-frame")
def last_frame():
    from fastapi import HTTPException, Response
    import cv2

    cap = camera_controller.get_cap()
    if cap is None:
        status = camera_controller.get_status()
        raise HTTPException(status_code=404, detail=f"Camera belum siap: {status.get('last_error')}")

    ok, frame = camera_controller.read_frame()
    if not ok or frame is None:
        raise HTTPException(status_code=409, detail="Gagal membaca frame terbaru.")

    ok2, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
    if not ok2:
        raise HTTPException(status_code=500, detail="Gagal encode frame.")

    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Connection": "keep-alive",
    }
    return Response(content=buf.tobytes(), media_type="image/jpeg", headers=headers)