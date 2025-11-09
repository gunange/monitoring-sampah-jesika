from fastapi import APIRouter
from fastapi.responses import StreamingResponse

camera_router = APIRouter()

@camera_router.get("/camera/stream")
def stream():
    # Lazy import untuk hindari circular import dan akses state terpusat
    from ml.app.config import get_int, get_str
    from ml.app.camera import parse_camera_src, open_capture
    from ml.app import services as service
    
    import cv2, time
    status = {}
    src = parse_camera_src()
    backend = get_str("CAMERA_BACKEND", "AVFOUNDATION")
    cap = open_capture(src, backend, status, service.logger)
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