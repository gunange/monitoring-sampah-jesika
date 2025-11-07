from fastapi import APIRouter
from fastapi.responses import StreamingResponse

stream_router = APIRouter()

@stream_router.get("/stream")
def stream():
    # Lazy import untuk hindari circular import dan akses state terpusat
    from pathlib import Path
    from ml.app.config import get_str, get_int
    from ml.app.knn import train_knn_from_dataset_json, load_knn
    from ml.app import service as service

    # Auto-start worker jika kamera belum terbuka
    try:
        st = dict(service._camera_status)
        if not st.get("open"):
            service.start_worker()
    except Exception:
        pass

    # Auto-train KNN: jika belum loaded dan dataset siap, latih dari dataset.json
    try:
        with service._state_lock:
            knn_loaded = service._knn_model is not None
        if not knn_loaded:
            counts = service.dataset_counts()
            total = counts.get("TOTAL", counts.get("BERSIH", 0) + counts.get("ADA_SAMPAH", 0) + counts.get("SAMPAH_MENUMPUK", 0))
            if total > 0:
                out_path = Path(get_str("KNN_MODEL_PATH", "ml/models/knn.joblib"))
                n_neighbors = get_int("KNN_NEIGHBORS", 3)
                model_file = train_knn_from_dataset_json(
                    dataset_path=service.get_dataset_json(),
                    out_path=out_path,
                    n_neighbors=n_neighbors,
                )
                model = load_knn(model_file)
                with service._state_lock:
                    service._knn_model = model
    except Exception as e:
        # Jangan blokir stream jika auto-train gagal
        try:
            service.logger.warning(f"Auto-train KNN dilewati: {e}")
        except Exception:
            pass

    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Connection": "keep-alive",
    }
    return StreamingResponse(
        service.mjpeg_from_latest(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers=headers,
    )

@stream_router.get("/stream/metrics")
def stream_metrics():
    # Lazy import untuk hindari circular import
    from ml.app.service import _state_lock, _latest_metrics
    # Ambil metrik terbaru dari worker kamera
    with _state_lock:
        m = dict(_latest_metrics)
    trash_pct = float(m.get("trashPct") or 0.0)
    pre_knn_conf = round(trash_pct / 100.0, 4)  # 0.0 - 1.0
    return {
        "ts": m.get("ts"),
        "trashPct": trash_pct,
        "preKnnConfidence": pre_knn_conf,
        "suppressed": bool(m.get("suppressed", False)),
        "knnLabel": m.get("knnLabel"),
        "knnConfidence": m.get("knnConfidence"),
    }

