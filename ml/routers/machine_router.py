from fastapi import APIRouter

machine_router = APIRouter()

@machine_router.get("/machine-learning")
def machine_learning():
    from ml.services.main_service import camera_controller, machine_learning_controller

    running = True;
    if camera_controller.get_cap() is None:
        running = False
    if not machine_learning_controller.status:
        running = False

    return {"name": "Machine Learning", "running": running}


@machine_router.get("/machine-learning/start")
def start_machine_learning():
    from ml.services.main_service import camera_controller, dataset_controller, machine_learning_controller

    dataset_controller.initSetDataFromDb()
    camera_controller.start()
    machine_learning_controller.status = True

    return {"name": "Machine Learning", "running": True}

@machine_router.get("/machine-learning/stop")
def stop_machine_learning():
    from ml.services.main_service import camera_controller, dataset_controller, machine_learning_controller

    dataset_controller.dataset = []
    camera_controller.stop()
    machine_learning_controller.status = False

    return {"name": "Machine Learning", "running": False}

