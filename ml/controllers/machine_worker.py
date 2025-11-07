# controllers/machine_worker.py
import threading
from dataclasses import dataclass
from typing import Callable, Any
from datetime import datetime

@dataclass
class MachineContext:
    state_lock: threading.Lock
    machine_status: dict
    get_int: Callable[[str, int], int]
    get_str: Callable[[str, str], str]
    get_raw_frame_jpeg: Callable[[], Any]
    save_detection_and_dataset: Callable[[bytes, str, Any, float, tuple], dict]
    decode_jpeg_to_bgr: Callable[[bytes], Any]
    compute_metrics: Callable[[Any], dict]
    knn_model_getter: Callable[[], Any]
    logger: Any

def get_machine_interval_min(ctx: MachineContext) -> int:
    return max(1, ctx.get_int("MACHINE_INTERVAL_MINUTES", 5))

def machine_worker(stop_event: threading.Event, ctx: MachineContext):
    interval_min = get_machine_interval_min(ctx)
    with ctx.state_lock:
        ctx.machine_status.update({"running": True, "interval_min": interval_min})
    try:
        while not stop_event.is_set():
            raw_jpeg = ctx.get_raw_frame_jpeg()
            result = None
            try:
                knn_label, knn_conf = None, None
                trash_pct, suppressed, rx, ry, rw, rh = 0.0, False, 0, 0, 0, 0
                if raw_jpeg:
                    bgr = ctx.decode_jpeg_to_bgr(raw_jpeg)
                    if bgr is not None:
                        m = ctx.compute_metrics(bgr)
                        trash_pct = m["trash_pct"]
                        suppressed = m["suppressed"]
                        rx, ry, rw, rh = m["roi"]
                        # KNN pada ROI jika tersedia
                        knn_model = ctx.knn_model_getter()
                        if knn_model is not None and not suppressed:
                            try:
                                roi_img = bgr[ry:ry+rh, rx:rx+rw] if rw > 0 and rh > 0 else bgr
                                # Hindari import dari service.py untuk mencegah circular import
                                from ml.app.knn import predict_knn  # sesuai struktur repo Anda
                                knn_label, knn_conf = predict_knn(knn_model, roi_img)
                            except Exception as e:
                                ctx.logger.error(f"KNN infer error: {e}")
                # Keputusan label akhir (selaras dengan stream worker)
                thr = ctx.get_int("ALERT_THRESHOLD", 12)
                is_trash = (trash_pct >= thr) or (knn_label == "ADA_SAMPAH")

                # Keputusan label akhir: HANYA KNN
                positive_labels = {"ADA_SAMPAH", "ADA SAMPAH", "SAMPAH MENUMPUK", "SAMPAH_MENUMPUK"}
                is_trash = (knn_label in positive_labels) and (not suppressed)

                # Normalisasi label untuk penyimpanan dataset (tetap "ADA SAMPAH" demi kompatibilitas)
                if suppressed:
                    label_norm = "BERSIH"
                else:
                    label_norm = "ADA SAMPAH" if is_trash else "BERSIH"

                save_info = {"ok": False}
                log_clean = ctx.get_str("SAVE_LOG_BERSIH", "false").lower() in {"1","true","yes","y"}
                should_save = (not suppressed) and (is_trash or log_clean)
                if raw_jpeg and should_save:
                    save_info = ctx.save_detection_and_dataset(
                        raw_jpeg, label_norm, knn_conf, trash_pct, (rx, ry, rw, rh)
                    )

                result = {
                    "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                    "label": label_norm,
                    "knnConfidence": knn_conf,
                    "trashPct": round(trash_pct, 2),
                    "suppressed": suppressed,
                    "saved": save_info,
                }
            except Exception as e:
                ctx.logger.error(f"Machine run error: {e}")
                result = {"ok": False, "error": str(e)}

            with ctx.state_lock:
                ctx.machine_status.update({
                    "last_run": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                    "run_count": int(ctx.machine_status.get("run_count", 0)) + 1,
                    "last_result": result,
                    "interval_min": interval_min,
                })

            if stop_event.wait(interval_min * 60):
                break
    finally:
        with ctx.state_lock:
            ctx.machine_status.update({"running": False})