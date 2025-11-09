from fastapi import APIRouter
from fastapi.responses import StreamingResponse

camera_router = APIRouter()

@camera_router.get("/camera")
def camera_status():
    from ml.app.camera import controller
    return controller.get_status()

@camera_router.get("/camera/list")
def camera_list():
    from ml.app.config import get_int, get_str
    from ml.app.camera import open_capture
    from ml.app import services as service

    backend = get_str("CAMERA_BACKEND", "AVFOUNDATION")
    max_scan = max(1, get_int("CAMERA_SCAN_MAX", 5))  # default scan 5 indeks
    cameras = []
    for idx in range(max_scan):
        status = {}
        cap = open_capture(idx, backend, status, service.logger)
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
    from ml.app.camera import controller
    ok = controller.start()
    return {"started": ok, "status": controller.get_status()}

@camera_router.get("/camera/stop")
def camera_stop():
    from ml.app.camera import controller
    controller.stop()
    return {"stopped": True, "status": controller.get_status()}

@camera_router.get("/camera/stream")
def stream():
    # Lazy import untuk hindari circular import dan akses state terpusat
    from fastapi import HTTPException
    from ml.app.config import get_int
    from ml.app.camera import controller
    import cv2, time

    cap = controller.get_cap()
    if cap is None:
        controller.start()
        cap = controller.get_cap()
        if controller.get_cap() is None:
            status = controller.get_status()
            raise HTTPException(status_code=409, detail=f"Camera gagal start: {status.get('last_error')}")

    fps = max(1, get_int("STREAM_FPS", 10))
    w = get_int("STREAM_WIDTH", 1280)
    h = get_int("STREAM_HEIGHT", 720)
    try:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    except Exception:
        pass

    boundary = b"--frame\r\n"
    def gen():
        try:
            while True:
                ok, frame = cap.read()
                if not ok or frame is None:
                    break
                try:
                    if w and h:
                        frame = cv2.resize(frame, (w, h), interpolation=cv2.INTER_AREA)
                except Exception:
                    pass
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
            # Jangan release di sini; controller mengelola lifecycle.
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