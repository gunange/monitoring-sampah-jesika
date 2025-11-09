import cv2
from typing import Any
from ml.app.config import get_str


BACKENDS = {
    "ANY": int(cv2.CAP_ANY),
    "AVFOUNDATION": int(cv2.CAP_AVFOUNDATION),  # macOS
}

def parse_camera_src():
    s = get_str("CAMERA_SRC", "0")
    try:
        return int(s)
    except ValueError:
        return s

def open_capture(src, backend_name: str | None, camera_status: dict, logger: Any):
    tried = []
    def try_backend(name: str | None):
        cap = cv2.VideoCapture(src, BACKENDS.get(name.upper(), cv2.CAP_ANY)) if name else cv2.VideoCapture(src)
        label = name or "DEFAULT"
        tried.append(label)
        if cap is None or not cap.isOpened():
            try:
                if cap: cap.release()
            except Exception:
                pass
            return None
        ok, _ = cap.read()
        if not ok:
            try:
                cap.release()
            except Exception:
                pass
            return None
        camera_status.update({"open": True, "src": src, "backend": label, "last_error": None})
        return cap

    cap = None
    if backend_name:
        cap = try_backend(backend_name)
    if cap is None:
        for name in ["AVFOUNDATION", "ANY", None]:
            if backend_name and (name == backend_name or (name is None and backend_name is None)):
                continue
            cap = try_backend(name)
            if cap:
                break

    if cap is None:
        camera_status.update({
            "open": False,
            "src": src,
            "backend": backend_name,
            "last_error": f"OpenCV gagal membuka kamera. Dicoba: {tried}. Periksa izin kamera & apakah sedang dipakai app lain."
        })
        if logger:
            logger.error(f"Gagal membuka kamera src={src} backend={backend_name}. Dicoba: {tried}")
        return None
    return cap

class CameraController:
    def __init__(self):
        self.cap = None
        self.status = {"open": False, "src": None, "backend": None, "last_error": None}
        self.running = False

    def start(self) -> bool:
        from ml.app.services import logger
        
        if self.cap and self.running:
            return True    
        src = parse_camera_src()
        backend_name = get_str("CAMERA_BACKEND", "AVFOUNDATION")
        cap = open_capture(src, backend_name, self.status, logger)
        if cap is None:
            self.cap = None
            self.running = False
            return False
        self.cap = cap
        self.running = True
        return True

    def stop(self) -> None:
        self.running = False
        try:
            if self.cap:
                self.cap.release()
        except Exception:
            pass
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
