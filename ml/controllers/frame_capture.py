import cv2, time
import threading
from dataclasses import dataclass
from typing import Callable, Any

from ml.app.camera_open import parse_camera_src, open_capture

@dataclass
class FrameCaptureContext:
    state_lock: threading.Lock
    latest_raw_jpeg_getter: Callable[[], bytes | None]
    get_int: Callable[[str, int], int]
    get_str: Callable[[str, str], str]
    logger: Any
    camera_status_ref: dict

def get_raw_frame_jpeg(ctx: FrameCaptureContext) -> bytes | None:
    # Ambil dari buffer stream jika ada
    live = None
    with ctx.state_lock:
        live = ctx.latest_raw_jpeg_getter()
    if live:
        return live

    src = parse_camera_src()
    backend = ctx.get_str("CAMERA_BACKEND", "AVFOUNDATION")
    cap = open_capture(src, backend, ctx.camera_status_ref, ctx.logger)
    if cap is None:
        return None
    try:
        warm_frames = max(10, ctx.get_int("CAPTURE_WARM_FRAMES", 15))
        for _ in range(warm_frames):
            ok_w, _ = cap.read()
            if not ok_w:
                break
            time.sleep(0.02)
        ok, frame = cap.read()
    finally:
        try:
            cap.release()
        except Exception:
            pass
    if not ok or frame is None:
        return None
    ok_raw, raw_jpeg = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    if not ok_raw:
        return None
    return raw_jpeg.tobytes()