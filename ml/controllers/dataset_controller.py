from typing import Dict, Any


# class DatasetController:
class DatasetController:
    def __init__(self):
        pass

    def store(self, label: str) -> Dict[str, Any]:
        from fastapi import HTTPException
        import json
        from ml.controllers.frame_controller import frame_controller
        from ml.lib.api_request_lib import post as api_post
        from ml.app.logging import logger

        data = frame_controller.capture_features(label=label, return_image=True)
        if not data.get("ok"):
            # Log kegagalan capture
            logger.error("capture_features gagal: %s", data.get("reason"))
            raise HTTPException(status_code=409, detail={"error": data.get("reason")})

        api_path = "machine-learning/dataset"

        try:
            # Bentuk payload JSON sesuai validator (angka & objek)
            features = data.get("features", {}) or {}
            frame = data.get("frame", {}) or {}
            roi = data.get("roi", {}) or {}

            payload = {
                "label": data.get("label", "UNKNOW"),
                "h_mean": float(features.get("h_mean", 0.0)),
                "h_std": float(features.get("h_std", 0.0)),
                "s_mean": float(features.get("s_mean", 0.0)),
                "s_std": float(features.get("s_std", 0.0)),
                "v_mean": float(features.get("v_mean", 0.0)),
                "v_std": float(features.get("v_std", 0.0)),
                "laplacian_var": float(features.get("laplacian_var", 0.0)),
                "edge_ratio": float(features.get("edge_ratio", 0.0)),
                "shape_area_ratio": float(features.get("shape_area_ratio", 0.0)),
                "frame": {
                    "width": int(frame.get("width", 0)),
                    "height": int(frame.get("height", 0)),
                },
                "roi": {
                    "x": int(roi.get("x", 0)),
                    "y": int(roi.get("y", 0)),
                    "w": int(roi.get("w", 0)),
                    "h": int(roi.get("h", 0)),
                },
            }

            # Multipart: kirim file + satu part JSON di field "form"
            files = {}
            img_bytes = data.get("image_bytes")
            if img_bytes:
                files["file"] = ("frame.jpg", img_bytes, "image/jpeg")

            # Kirim ke API; HeandleRequest.parse akan baca body.form lalu JSON.parse
            resp = api_post(api_path, data={"form": json.dumps(payload)}, files=files)

            # Tangani respons success/error
            if 200 <= resp.status_code < 300:
                try:
                    return resp.json()
                except Exception:
                    return {"statusCode": resp.status_code, "body": resp.text}

            try:
                detail = resp.json()
            except Exception:
                detail = {"error": resp.text}
            logger.error(
                "Upstream API error %s pada path %s, label=%s, detail=%s",
                resp.status_code, api_path, label, detail,
            )
            raise HTTPException(status_code=resp.status_code, detail=detail)

        except Exception as e:
            logger.exception("DatasetController.store exception saat POST ke %s", api_path)
            raise HTTPException(
                status_code=502,
                detail={"error": "Failed to post dataset to API", "reason": str(e)},
            )
