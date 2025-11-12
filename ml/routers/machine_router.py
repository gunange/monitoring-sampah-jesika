from fastapi import APIRouter

machine_router = APIRouter()


@machine_router.get("/machine-learning")
def machine_learning():
    from ml.services.main_service import (
        camera_controller,
        machine_learning_controller,
        knn_service,
        dataset_controller
    )

    from ml.lib.camera import get_camera_list

    running = True
    if camera_controller.get_cap() is None:
        running = False
    elif not machine_learning_controller.status:
        running = False
    elif not knn_service._running:
        running = False

    dataset_controller.initSetDataFromDb();
    camera_list = get_camera_list();

    return {
        "name": "Machine Learning",
        "running": running,
        "detail": {
            "camera": camera_controller.get_cap() is not None,
            "knn": knn_service._running,
            "dataset" : len(dataset_controller.dataset),
            "camera-list" : camera_list
        },
    }


@machine_router.get("/machine-learning/start")
async def start_machine_learning():
    from ml.services.main_service import (
        camera_controller,
        dataset_controller,
        machine_learning_controller,
        knn_service,
    )
    from ml.app.logging import logger

    dataset_controller.initSetDataFromDb()
    knn_service.fit_from_records(dataset_controller.dataset)
    camera_controller.start()

    # def on_result(pred, result):
    # knn_service.start(on_result=on_result)

    knn_service.start()
    machine_learning_controller.status = True

    # Samakan penilaian running dan detail seperti route /machine-learning
    from ml.lib.camera import get_camera_list
    running = True
    if camera_controller.get_cap() is None:
        running = False
    elif not machine_learning_controller.status:
        running = False
    elif not knn_service._running:
        running = False

    camera_list = get_camera_list()
    return {
        "name": "Machine Learning",
        "running": running,
        "detail": {
            "camera": camera_controller.get_cap() is not None,
            "knn": knn_service._running,
            "dataset": len(dataset_controller.dataset),
            "camera-list": camera_list,
        },
    }


@machine_router.get("/machine-learning/stop")
async def stop_machine_learning():
    from ml.services.main_service import (
        camera_controller,
        machine_learning_controller,
        knn_service,
    )

    camera_controller.stop()
    await knn_service.stop()
    machine_learning_controller.status = False

    running = True
    if camera_controller.get_cap() is None:
        running = False
    elif not machine_learning_controller.status:
        running = False
    elif not knn_service._running:
        running = False

    return {
        "name": "Machine Learning",
        "running": running,
        "detail": {
            "camera": camera_controller.get_cap() is not None,
            "knn": knn_service._running,
            "dataset": 0,
            "camera-list": 0,
        },
    }
