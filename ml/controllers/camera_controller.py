import threading

from ml.app.logging import logger


class CameraController:
    def __init__(self):
        self.cap = None
        self.status = {"open": False, "src": None, "backend": None, "last_error": None}
        self.running = False
        self.lock = threading.RLock()
        logger.info("CameraController diinisialisasi")

    def start(self) -> bool:
        from ml.lib.camera import parse_camera_src, open_capture
        from ml.app.config import get_str

        with self.lock:
            if self.cap and self.running:
                logger.info("Start diabaikan: kamera sudah berjalan")
                return True
            src = parse_camera_src()
            backend_name = get_str("CAMERA_BACKEND", "AVFOUNDATION")
            logger.info(f"Memulai kamera src={src} backend={backend_name}")
            cap = open_capture(src, backend_name, self.status)
            if cap is None:
                self.cap = None
                self.running = False
                logger.error("Start gagal: tidak bisa membuka kamera")
                return False
            self.cap = cap
            self.running = True
            logger.info("Kamera berjalan")
            return True

    def stop(self) -> None:
        with self.lock:
            logger.info("Menghentikan kamera")
            self.running = False
            try:
                if self.cap:
                    self.cap.release()
            except Exception as e:
                logger.error(f"Kesalahan saat melepas kamera: {e}")
            self.cap = None
            self.status.update({"open": False})

    def get_cap(self):
        return self.cap if self.running and self.cap is not None else None

    def get_status(self):
        return {
            "running": self.running,
            "open": bool(self.cap),
            "src": self.status.get("src"),
            "backend": self.status.get("backend"),
            "last_error": self.status.get("last_error"),
        }

    def read_frame(self):
        with self.lock:
            if not self.running or self.cap is None:
                return False, None
            ok, frame = self.cap.read()
            if not ok:
                logger.info("read_frame: gagal membaca frame dari kamera")
            return ok, frame
