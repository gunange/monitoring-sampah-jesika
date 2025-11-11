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

        data = frame_controller.capture_features(label=label, return_image=True)
        if not data.get("ok"):
            # Biarkan handler global yang log ke error.log
            raise HTTPException(status_code=409, detail={"error": data.get("reason")})

        api_path = "machine-learning/dataset"

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

        resp = api_post(api_path, data={"form": json.dumps(payload)}, files=files)

        # Sederhana: jika tidak sukses, lempar HTTPException dan biarkan handler global yang log
        if not (200 <= resp.status_code < 300):
            # Jika upstream mengembalikan JSON dengan "error", pakai itu; fallback ke text
            try:
                body = resp.json()
            except Exception:
                body = {"error": resp.text}
            raise HTTPException(status_code=resp.status_code, detail=body)

        try:
            return (resp.json())["data"]
        except Exception:
            return {"statusCode": resp.status_code, "body": resp.text}
