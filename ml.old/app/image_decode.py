import numpy as np
import cv2

def decode_jpeg_to_bgr(jpeg_bytes: bytes):
    try:
        arr = np.frombuffer(jpeg_bytes, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return img
    except Exception:
        return None