# Router baru untuk operasi machine: start/stop/status

from fastapi import APIRouter

machine_router = APIRouter()

@machine_router.get("/machine/start")
def machine_start():
    # Lazy import untuk hindari circular import
    from ml.app.service import start_machine, start_worker, get_machine_status
    # Aktifkan kamera (worker) lalu mulai scheduler monitoring
    start_worker()
    start_machine()
    return {"ok": True, "status": get_machine_status()}

@machine_router.get("/machine/stop")
def machine_stop():
    # Lazy import untuk hindari circular import
    from ml.app.service import stop_machine, stop_worker, get_machine_status
    # Hentikan scheduler monitoring dan kamera
    stop_machine()
    stop_worker()
    return {"ok": True, "status": get_machine_status()}

@machine_router.get("/machine/status")
def machine_status():
    # Lazy import untuk hindari circular import
    from ml.app.service import get_machine_status
    return get_machine_status()