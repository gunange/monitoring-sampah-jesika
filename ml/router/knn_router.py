from fastapi import APIRouter

knn_router = APIRouter()

@knn_router.get("/knn/status")
def knn_status():
    # Lazy import untuk hindari circular import
    from ml.app.config import get_str
    from ml.app.service import _knn_model
    return {
        "enabled": get_str("KNN_ENABLED", "true").lower() in {"1","true","yes","y"},
        "loaded": _knn_model is not None,
        "modelPath": get_str("KNN_MODEL_PATH", "ml/models/knn.joblib"),
    }

@knn_router.post("/knn/train")
def knn_train(payload: dict):
    from pathlib import Path
    from ml.app.config import get_str, get_int
    from ml.app.service import _state_lock, _knn_model, dataset_counts, get_dataset_json
    from ml.app.knn import train_knn_from_dataset_json, load_knn
    neighbors = int(payload.get("neighbors", get_int("KNN_NEIGHBORS", 5)))
    out_path = Path(payload.get("out", get_str("KNN_MODEL_PATH", "ml/models/knn.joblib")))
    dataset_path = get_dataset_json()
    counts = dataset_counts()
    total = counts.get("TOTAL", counts.get("BERSIH", 0) + counts.get("ADA_SAMPAH", 0))
    if total == 0:
        return {"ok": False, "error": "Dataset kosong. Tambah data latih dulu via /dataset."}
    try:
        out = train_knn_from_dataset_json(dataset_path=dataset_path, out_path=out_path, n_neighbors=neighbors)
        model = load_knn(out)
        with _state_lock:
            _knn_model = model
        return {"ok": True, "modelPath": str(out), "neighbors": neighbors, "dataset": counts}
    except Exception as e:
        return {"ok": False, "error": f"Gagal training: {e}"}

@knn_router.post("/knn/reload")
def knn_reload():
    # Lazy import untuk hindari circular import
    from pathlib import Path
    from ml.app.config import get_str
    from ml.app.service import _state_lock, _knn_model
    from ml.app.knn import load_knn

    try:
        p = Path(get_str("KNN_MODEL_PATH", "ml/models/knn.joblib"))
        if not p.exists():
            return {"ok": False, "error": f"Model tidak ditemukan: {p}"}
        model = load_knn(p)
        with _state_lock:
            _knn_model = model
        return {"ok": True, "modelPath": str(p)}
    except Exception as e:
        return {"ok": False, "error": f"Gagal reload: {e}"}