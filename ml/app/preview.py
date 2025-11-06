import cv2
from .config import get_int
from .utils import get_logger
from pathlib import Path

def main():
    src = get_int("CAMERA_SRC", 0)
    logger = get_logger("preview", Path("ml/logs/ml_service.log"))
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        raise RuntimeError(f"Gagal membuka kamera/stream: {src}")
    cv2.namedWindow("Preview", cv2.WINDOW_NORMAL)
    try:
        while True:
            ok, frame = cap.read()
            if not ok or frame is None:
                logger.error("Frame tidak terbaca")
                continue
            cv2.imshow("Preview", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()