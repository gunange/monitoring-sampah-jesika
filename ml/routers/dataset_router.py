# module dataset_router
from fastapi import APIRouter, Body
import json

dataset_router = APIRouter()


@dataset_router.post("/dataset")
def _add(
    label: str = Body("UNKNOW", embed=True),
):
    from fastapi import HTTPException
    from ml.controllers.frame_controller import frame_controller
    from ml.lib.api_request_lib import post as api_post
    from ml.app.config import get_str

    data = frame_controller.capture_features(label=label, return_image=True)
    if not data.get("ok"):
        raise HTTPException(status_code=409, detail={"error": data.get("reason")})

    api_path = "machine-learning/dataset"

    try:
        # Siapkan multipart form-data
        form = {
            "label": data.get("label", "UNKNOW"),
            "features": json.dumps(data.get("features", {})),
            "image_path": data.get("image_path", ""),
            "frame_w": str(data.get("frame", {}).get("width", "")),
            "frame_h": str(data.get("frame", {}).get("height", "")),
        }
        files = None
        img_bytes = data.get("image_bytes")
        if img_bytes:
            files = {"file": ("frame.jpg", img_bytes, "image/jpeg")}
        # Kirim ke API
        resp = api_post(api_path, data=form, files=files)
        data["api_status_code"] = resp.status_code
        try:
            data["api_response"] = resp.json()
        except Exception:
            data["api_response_text"] = resp.text
    except Exception as e:
        data["post_error"] = str(e)

    # Sanitasi field bytes agar JSON encoder tidak error
    if "image_bytes" in data:
        try:
            data["image_bytes_len"] = len(data["image_bytes"]) if data["image_bytes"] else 0
        finally:
            data.pop("image_bytes", None)

    return data
