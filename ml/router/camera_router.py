from fastapi import APIRouter

camera_router = APIRouter()

@camera_router.post("/camera")
def set_camera(payload: dict):
    # Lazy import untuk hindari circular import
    import os
    from ml.app.service import start_worker, logger
    src = str(payload.get("src", "0"))
    backend = str(payload.get("backend", "AVFOUNDATION"))
    os.environ["CAMERA_SRC"] = src
    os.environ["CAMERA_BACKEND"] = backend
    logger.info(f"Set camera requested: src={src}, backend={backend}. Restarting worker.")
    start_worker()
    return {"ok": True, "src": src, "backend": backend}

@camera_router.post("/camera/stop")
def camera_stop():
    # Lazy import untuk hindari circular import
    import time
    from ml.app.service import _worker_stop
    if _worker_stop:
        _worker_stop.set()
        time.sleep(0.3)
    return {"ok": True}

@camera_router.get("/diag/camera")
def diag_camera(src: str | None = None):
    # Lazy import untuk hindari circular import
    import cv2
    from ml.app.service import parse_camera_src, BACKENDS
    test_src = int(src) if src is not None and str(src).isdigit() else parse_camera_src()
    results = []
    for name in ["AVFOUNDATION", "ANY", None]:
        label = name or "DEFAULT"
        err = None
        opened = False
        read_ok = False
        try:
            cap = cv2.VideoCapture(test_src, BACKENDS.get(name.upper(), cv2.CAP_ANY)) if name else cv2.VideoCapture(test_src)
            opened = bool(cap and cap.isOpened())
            if opened:
                ok, _ = cap.read()
                read_ok = bool(ok)
            if cap:
                cap.release()
        except Exception as e:
            err = str(e)
        results.append({"backend": label, "opened": opened, "read_ok": read_ok, "error": err})
    return {"src": test_src, "results": results}