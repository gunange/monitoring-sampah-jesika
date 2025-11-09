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

@stream_router.get("/stream/v2")
def stream_v2():
    # Lazy import untuk hindari circular import dan akses state terpusat
    from pathlib import Path
    from ml.app.config import get_int, get_str
    from ml.app.camera_open import parse_camera_src, open_capture
    from ml.app import service as service
    import cv2, time
    status = {}
    src = parse_camera_src()
    backend = get_str("CAMERA_BACKEND", "AVFOUNDATION")
    cap = open_capture(src, backend, status, service.logger)
    fps = max(1, get_int("STREAM_FPS", 10))
    w = get_int("STREAM_WIDTH", 1280)
    h = get_int("STREAM_HEIGHT", 720)
    try:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    except Exception:
        pass
    boundary = b"--frame\r\n"
    def gen():
        try:
            while True:
                ok, frame = cap.read()
                if not ok or frame is None:
                    break
                try:
                    if w and h:
                        frame = cv2.resize(frame, (w, h), interpolation=cv2.INTER_AREA)
                except Exception:
                    pass
                ok2, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
                if not ok2:
                    continue
                b = buf.tobytes()
                yield (boundary +
                       b"Content-Type: image/jpeg\r\n" +
                       b"Content-Length: " + str(len(b)).encode() + b"\r\n\r\n" +
                       b + b"\r\n")
                time.sleep(1.0 / float(fps))
        finally:
            try:
                cap.release()
            except Exception:
                pass
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Connection": "keep-alive",
    }
    return StreamingResponse(
        gen(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers=headers,
    )

