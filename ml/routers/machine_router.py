from fastapi import APIRouter

machine_router = APIRouter()

@machine_router.get("/machine-learning")
def machine_learning():
    from ml.app.services import camera_service

    running = True;
    if camera_service.get_cap() is None:
        running = False

    return {"name": "Machine Learning", "running": running}


@machine_router.get("/machine-learning/start")
def start_machine_learning():
    from ml.app.services import camera_service

    camera_service.start()

    return {"name": "Machine Learning", "running": True}

@machine_router.get("/machine-learning/stop")
def stop_machine_learning():
    from ml.app.services import camera_service

    camera_service.stop()

    return {"name": "Machine Learning", "running": False}

