# Router baru untuk operasi machine: start/stop/status

from fastapi import APIRouter
from ml.app.config import get_int

camera_router = APIRouter()

@camera_router.get("/camera/start")
def machine_start():
    # Lazy import untuk hindari circular import
    from ml.app.service import start_machine, start_worker, get_machine_status
    # Aktifkan kamera (worker) lalu mulai scheduler monitoring
    start_worker()
    start_machine()
    return {"ok": True, "status": get_machine_status()}

@camera_router.get("/camera/stop")
def machine_stop():
    # Lazy import untuk hindari circular import
    from ml.app.service import stop_machine, stop_worker, get_machine_status
    # Hentikan scheduler monitoring dan kamera
    stop_machine()
    stop_worker()
    return {"ok": True, "status": get_machine_status()}

@camera_router.get("/camera/status")
def machine_status():
    # Lazy import untuk hindari circular import
    from ml.app.service import get_machine_status, _camera_status
    from ml.app.config import get_str, get_int
    status = get_machine_status()
    return {
        "machine": status,
        "camera": {
            "env_src": get_str("CAMERA_SRC", "0"),
            "env_backend": get_str("CAMERA_BACKEND", "AVFOUNDATION"),
            "env_stream_fps": get_int("STREAM_FPS", 10),
            "live": _camera_status,
        },
    }

@camera_router.get("/camera/list")
def camera_list(max_index: int | None = None):
    import cv2
    from ml.app.service import BACKENDS
    from ml.app.config import get_int
    # Pakai env CAMERA_LIST_MAX jika param tidak diberikan
    scan_max = max_index if max_index is not None else get_int("CAMERA_LIST_MAX", 5)
    cams = []
    for idx in range(scan_max + 1):
        opened = False
        read_ok = False
        backend_used = None
        err = None
        try:
            for name in ["AVFOUNDATION", "ANY", None]:
                cap = cv2.VideoCapture(idx, BACKENDS.get(name.upper(), cv2.CAP_ANY)) if name else cv2.VideoCapture(idx)
                if cap and cap.isOpened():
                    ok, _ = cap.read()
                    if ok:
                        opened = True
                        read_ok = True
                        backend_used = name or "DEFAULT"
                        cap.release()
                        break
                if cap:
                    cap.release()
        except Exception as e:
            err = str(e)
        cams.append({"index": idx, "opened": opened, "read_ok": read_ok, "backend": backend_used, "error": err})
    return {"cameras": cams}

@camera_router.get("/camera/set")
def camera_set(src: str, backend: str | None = None):
    import os
    from ml.app.service import stop_worker, start_worker
    # Update env di runtime agar dibaca oleh parse_camera_src()
    os.environ["CAMERA_SRC"] = src
    if backend:
        os.environ["CAMERA_BACKEND"] = backend
    # Restart worker agar src baru dipakai
    stop_worker()
    start_worker()
    return {"ok": True, "src": src, "backend": backend or os.getenv("CAMERA_BACKEND", "AVFOUNDATION")}


def config_reload():
    # Reload .env dan restart worker agar STREAM_FPS/CAMERA_SRC baru terpakai
    from pathlib import Path
    from ml.app.config import load_env, get_str, get_int
    from ml.app.service import stop_worker, start_worker
    load_env(Path(__file__).resolve().parents[1] / ".env")
    stop_worker()
    start_worker()
    return {
        "ok": True,
        "config": {
            "CAMERA_SRC": get_str("CAMERA_SRC", "0"),
            "CAMERA_BACKEND": get_str("CAMERA_BACKEND", "AVFOUNDATION"),
            "STREAM_FPS": get_int("STREAM_FPS", 10),
            "CAMERA_LIST_MAX": get_int("CAMERA_LIST_MAX", 5),
        },
    }
