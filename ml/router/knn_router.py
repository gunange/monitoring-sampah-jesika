from fastapi import APIRouter
from pathlib import Path
from ml.app.config import get_str, get_int
from ml.app.service import _state_lock, _knn_model
from ml.app.service import dataset_counts
from ml.app.knn import train_knn, load_knn

knn_router = APIRouter()

@knn_router.get("/knn/status")
def knn_status():
    return {
        "enabled": get_str("KNN_ENABLED", "true").lower() in {"1","true","yes","y"},
        "loaded": _knn_model is not None,
        "modelPath": get_str("KNN_MODEL_PATH", "ml/models/knn.joblib"),
    }

@knn_router.post("/knn/train")
def knn_train(payload: dict):
    neighbors = int(payload.get("neighbors", get_int("KNN_NEIGHBORS", 5)))
    out_path = Path(payload.get("out", get_str("KNN_MODEL_PATH", "ml/models/knn.joblib")))
    root = Path(payload.get("root", "ml/data/labeled"))

    counts = dataset_counts()
    if (counts["BERSIH"] + counts["ADA_SAMPAH"]) == 0:
        return {"ok": False, "error": "Dataset kosong. Tambah data latih dulu."}

    try:
        out = train_knn(labeled_root=root, out_path=out_path, n_neighbors=neighbors)
        model = load_knn(out)
        global _knn_model
        with _state_lock:
            _knn_model = model
        return {"ok": True, "modelPath": str(out), "neighbors": neighbors, "dataset": counts}
    except Exception as e:
        return {"ok": False, "error": f"Gagal training: {e}"}

@knn_router.post("/knn/reload")
def knn_reload():
    try:
        p = Path(get_str("KNN_MODEL_PATH", "ml/models/knn.joblib"))
        if not p.exists():
            return {"ok": False, "error": f"Model tidak ditemukan: {p}"}
        model = load_knn(p)
        global _knn_model
        with _state_lock:
            _knn_model = model
        return {"ok": True, "modelPath": str(p)}
    except Exception as e:
        return {"ok": False, "error": f"Gagal reload: {e}"}