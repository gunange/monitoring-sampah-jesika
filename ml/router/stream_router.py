from fastapi import APIRouter
from fastapi.responses import StreamingResponse

stream_router = APIRouter()

@stream_router.get("/stream")
def stream():
    # Lazy import untuk hindari circular import
    from ml.app.service import mjpeg_from_latest, start_worker, _camera_status
    # Auto-start worker jika kamera belum terbuka
    try:
        st = dict(_camera_status)
        if not st.get("open"):
            start_worker()
    except Exception:
        pass
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Connection": "keep-alive",
    }
    return StreamingResponse(
        mjpeg_from_latest(),
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
