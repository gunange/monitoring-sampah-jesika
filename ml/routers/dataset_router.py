# module dataset_router
from fastapi import APIRouter, Body
import json

dataset_router = APIRouter()


@dataset_router.post("/dataset")
def _add(
    label: str = Body("UNKNOW", embed=True),
):
    from ml.controllers.dataset_controller import DatasetController
    # Helper instance siap pakai
    dataset_controller = DatasetController()

    return dataset_controller.store(label)
