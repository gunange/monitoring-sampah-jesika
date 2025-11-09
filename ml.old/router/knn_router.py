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

@knn_router.get("/knn/train")
def knn_train(neighbors: int | None = None, out: str | None = None):
    from pathlib import Path
    from ml.app.config import get_str, get_int
    # Ganti cara impor agar assignment ke variabel modul bekerja
    from ml.app import service as service
    from ml.app.knn import train_knn_from_dataset_json, load_knn
    n_neighbors = int(neighbors if neighbors is not None else get_int("KNN_NEIGHBORS", 5))
    out_path = Path(out or get_str("KNN_MODEL_PATH", "ml/models/knn.joblib"))
    dataset_path = service.get_dataset_json()
    counts = service.dataset_counts()
    total = counts.get("TOTAL", counts.get("BERSIH", 0) + counts.get("ADA_SAMPAH", 0) + counts.get("SAMPAH_MENUMPUK", 0))
    if total == 0:
        return {"ok": False, "error": "Dataset kosong. Tambah data latih dulu via /dataset."}
    try:
        out_file = train_knn_from_dataset_json(dataset_path=dataset_path, out_path=out_path, n_neighbors=n_neighbors)
        model = load_knn(out_file)
        # Tulis ke atribut modul service, bukan ke nama lokal
        with service._state_lock:
            service._knn_model = model
        return {"ok": True, "modelPath": str(out_file), "neighbors": n_neighbors, "dataset": counts}
    except Exception as e:
        return {"ok": False, "error": f"Gagal training: {e}"}

@knn_router.post("/knn/reload")
def knn_reload():
    # Lazy import untuk hindari circular import
    from pathlib import Path
    from ml.app.config import get_str
    # Ganti ke modul service
    from ml.app import service as service
    from ml.app.knn import load_knn

    try:
        p = Path(get_str("KNN_MODEL_PATH", "ml/models/knn.joblib"))
        # Tambahkan guard: dataset harus siap
        counts = service.dataset_counts()
        total = counts.get("TOTAL", counts.get("BERSIH", 0) + counts.get("ADA_SAMPAH", 0) + counts.get("SAMPAH_MENUMPUK", 0))
        if total <= 0:
            return {"ok": False, "error": "Dataset kosong. Tidak bisa reload model."}
        if not p.exists():
            return {"ok": False, "error": f"Model tidak ditemukan: {p}"}
        model = load_knn(p)
        with service._state_lock:
            service._knn_model = model
        return {"ok": True, "modelPath": str(p)}
    except Exception as e:
        return {"ok": False, "error": f"Gagal reload: {e}"}