from fastapi import APIRouter

machine_router = APIRouter()


@machine_router.get("/machine-learning")
def machine_learning():
    from ml.services.main_service import (
        camera_controller,
        machine_learning_controller,
        knn_service,
        dataset_controller,
    )

    from ml.lib.camera import get_camera_list

    running = True
    if camera_controller.get_cap() is None:
        running = False
    elif not machine_learning_controller.status:
        running = False
    elif not knn_service._running:
        running = False

    dataset_controller.initSetDataFromDb()
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


@machine_router.get("/machine-learning/start")
async def start_machine_learning():
    from ml.services.main_service import (
        camera_controller,
        dataset_controller,
        machine_learning_controller,
        knn_service,
        knn_controller
    )
    from ml.app.logging import logger
    from ml.lib.camera import get_camera_list
    from collections import deque

    

    camera_list = get_camera_list()

    dataset_controller.initSetDataFromDb()
    knn_service.fit_from_records(dataset_controller.dataset)
    camera_controller.start()

    
    machine_learning_controller.status = True

    alert = deque(maxlen=50)
    alert_counter = 0
    def on_result(pred, result):
        nonlocal alert_counter
        if pred == "Sampah Menumpuk":
            alert_counter += 1
        else:
            alert_counter = 0 

        alert.append(pred)

        if alert_counter >= 10:
            knn_controller.send_alert_to_api(pred, result)
            logger.debug("⚠️ TERDETEKSI: Sampah Menumpuk berurutan 10 kali!, sudah dikirim ke API")
            alert_counter = 0

        logger.debug(f"⚠️ ALERT COUNTER: {alert_counter}")
    knn_service.start(on_result=on_result)
    # knn_service.start()

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
            "camera-list": [],
        },
    }
