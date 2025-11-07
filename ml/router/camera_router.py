# Router baru untuk operasi machine: start/stop/status

from fastapi import APIRouter

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
    from ml.app.service import get_machine_status
    return get_machine_status()