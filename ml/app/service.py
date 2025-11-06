# module: service.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, Response
import cv2
from .config import get_int

app = FastAPI()

@app.get("/")
def root():
    return {"service": "ml-service", "status": "ok"}

@app.get("/health")
def health():
    return {"status": "ok"}

def mjpeg_generator(src: int | str):
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        raise RuntimeError(f"Gagal membuka kamera/stream: {src}")
    try:
        while True:
            ok, frame = cap.read()
            if not ok or frame is None:
                continue
            ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            if not ok:
                continue
            frame_bytes = encoded.tobytes()
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n"
                   b"Content-Length: " + str(len(frame_bytes)).encode() + b"\r\n\r\n" +
                   frame_bytes + b"\r\n")
    finally:
        cap.release()

@app.get("/stream")
def stream():
    src = get_int("CAMERA_SRC", 0)
    return StreamingResponse(mjpeg_generator(src), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/frame")
def frame():
    src = get_int("CAMERA_SRC", 0)
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        raise RuntimeError(f"Gagal membuka kamera/stream: {src}")
    ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        raise RuntimeError("Gagal membaca frame")
    ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    if not ok:
        raise RuntimeError("Gagal encode frame")
    return Response(content=encoded.tobytes(), media_type="image/jpeg")