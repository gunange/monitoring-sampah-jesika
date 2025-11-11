from fastapi import APIRouter

machine_router = APIRouter()


@machine_router.get("/machine-learning")
def machine_learning():
    from ml.services.main_service import camera_controller, machine_learning_controller

    running = True
    if camera_controller.get_cap() is None:
        running = False
    if not machine_learning_controller.status:
        running = False

    return {"name": "Machine Learning", "running": running}


@machine_router.get("/machine-learning/start")
async def start_machine_learning():
    from ml.services.main_service import (
        camera_controller,
        dataset_controller,
        machine_learning_controller,
        knn_service,
    )

    dataset_controller.initSetDataFromDb()
    knn_service.fit_from_records(dataset_controller.dataset)
    camera_controller.start()
    knn_service.start()  # aman dipanggil dari context async, loop berjalan
    machine_learning_controller.status = True

    return {"name": "Machine Learning", "running": True}


@machine_router.get("/machine-learning/stop")
async def stop_machine_learning():
    from ml.services.main_service import (
        camera_controller,
        dataset_controller,
        machine_learning_controller,
        knn_service,
    )

    dataset_controller.dataset = []
    camera_controller.stop()
    await knn_service.stop()  # batalkan task loop dengan benar
    machine_learning_controller.status = False

    return {"name": "Machine Learning", "running": False}
