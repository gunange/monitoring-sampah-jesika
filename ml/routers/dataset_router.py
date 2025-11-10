# module dataset_router
from fastapi import APIRouter, Body

dataset_router = APIRouter()

@dataset_router.post("/dataset")
def get_frame(label: str = Body(..., embed=True)):
    from fastapi import HTTPException
    from ml.controllers.frame_controller import frame_controller

    data = frame_controller.capture_features()
    if not data.get("ok"):
        raise HTTPException(status_code=409, detail={
            "error": data.get("reason")
        })
    data["label"] = label
    return data