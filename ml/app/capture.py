# module: capture.py
import time
from pathlib import Path
import argparse
import cv2
import sys

# Import dengan fallback: mendukung run sebagai module (-m ml.app.capture)
# maupun langsung (python ml/app/capture.py)
try:
    from .config import get_int, get_str
    from .utils import ensure_dir, timestamp_str, get_logger
except ImportError:
    from app.config import get_int, get_str
    from app.utils import ensure_dir, timestamp_str, get_logger

def open_camera(src: int | str):
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        raise RuntimeError(f"Gagal membuka kamera/stream: {src}")
    return cap

def save_frame(frame, out_dir: Path, save_raw: bool = False) -> Path:
    ensure_dir(out_dir)
    latest_path = out_dir / "_latest.jpg"
    ok_latest = cv2.imwrite(str(latest_path), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    if not ok_latest:
        raise RuntimeError(f"Gagal menyimpan frame terbaru ke {latest_path}")

    # Opsional: simpan juga file timestamp jika diminta
    if save_raw:
        fname = f"{timestamp_str()}.jpg"
        out_path = out_dir / fname
        ok = cv2.imwrite(str(out_path), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        if not ok:
            raise RuntimeError(f"Gagal menyimpan frame ke {out_path}")
        return out_path

    return latest_path

def main(
    every_s: int | None = None,
    save_dir: Path | None = None,
    camera_src: int | str | None = None,
    save_raw: bool = False,
):
    # Ambil default dari ENV bila argumen tidak diberikan
    camera_src = camera_src if camera_src is not None else (get_int("CAMERA_SRC", 0))
    every_s = every_s if every_s is not None else get_int("SAMPLE_INTERVAL_S", 10)
    save_dir = save_dir if save_dir is not None else Path("ml/data/raw")

    logger = get_logger("capture", Path("ml/logs/ml_service.log"))
    logger.info(f"Mulai capture: src={camera_src}, interval={every_s}s, dir={save_dir}, save_raw={save_raw}")

    cap = open_camera(camera_src)
    try:
        while True:
            ok, frame = cap.read()
            if not ok or frame is None:
                logger.error("Frame tidak terbaca; menunggu 1s dan coba lagi")
                time.sleep(1)
                continue

            out_path = save_frame(frame, save_dir, save_raw=save_raw)
            if save_raw and out_path.name != "_latest.jpg":
                logger.info(f"Simpan RAW {out_path}")
            logger.info(f"Update latest {save_dir / '_latest.jpg'}")
            time.sleep(every_s)
    finally:
        cap.release()
        logger.info("Capture dihentikan")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capture frame berkala dari kamera.")
    parser.add_argument("--every", type=int, default=None, help="Interval detik (override ENV SAMPLE_INTERVAL_S)")
    parser.add_argument("--save-dir", type=Path, default=None, help="Folder output (default ml/data/raw)")
    parser.add_argument("--src", default=None, help="Sumber kamera: index (0) atau RTSP/URL")
    parser.add_argument("--save-raw", action="store_true", help="Simpan file mentah bertimestamp (default tidak menyimpan)")

    args = parser.parse_args()

    src_arg = args.src
    if src_arg is not None:
        try:
            src_arg = int(src_arg)
        except ValueError:
            pass

    main(every_s=args.every, save_dir=args.save_dir, camera_src=src_arg, save_raw=args.save_raw)