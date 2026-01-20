from fastapi import APIRouter
from ml.app.config import get_int

machine_router = APIRouter()


@machine_router.get("/machine-learning")
def machine_learning():
    from ml.services.main_service import machine_service
    return machine_service.status

@machine_router.get("/machine-learning/start")
async def start_machine_learning():
    from ml.services.main_service import (
        camera_controller,
        dataset_controller,
        knn_service,
        knn_controller
    )
    from ml.app.logging import logger
    from collections import deque
    from ml.services.main_service import machine_service

    alert = deque(maxlen=50)
    alert_counter = 0
    
    # Service Penting
    dataset_controller.initSetDataFromDb()
    try:
        knn_service.fit_from_records(dataset_controller.dataset)
    except Exception as e:
        logger.warning(f"Gagal melatih model KNN (mungkin dataset kosong): {e}")

    camera_controller.start()

    def on_result(pred, result):
        nonlocal alert_counter
        if pred == "Sampah Menumpuk":
            alert_counter += 1
        else:
            alert_counter = 0 

        alert.append(pred)

        if alert_counter >= get_int("ALERT_COUNT"):
            knn_controller.send_alert_to_api(pred, result)
            alert_counter = 0

    knn_service.start(on_result=on_result)
    
    machine_service.load_status()
    return machine_service.status


@machine_router.get("/machine-learning/stop")
async def stop_machine_learning():
    from ml.services.main_service import (
        camera_controller,
        knn_service,
    )
    from ml.services.main_service import machine_service

    camera_controller.stop()
    await knn_service.stop()

    machine_service.load_status()
    return machine_service.status
