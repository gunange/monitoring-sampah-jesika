import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Any

from ml.app.config import get_int, get_str
from ml.app.utils import ensure_dir
from ml.app.image_decode import decode_jpeg_to_bgr
from ml.app.image_features import extract_features_bgr

def get_detection_dir() -> Path:
    return Path(get_str("DETECT_SAVE_DIR", "ml/data/detections"))

def get_dataset_json() -> Path:
    return Path("ml/data/dataset.json")

def ensure_detection_dirs(logger: Any | None = None):
    try:
        detect_dir = get_detection_dir()
        ensure_dir(detect_dir)
        data_root = Path("ml/data")
        ensure_dir(data_root)
        dj = get_dataset_json()
        if not dj.exists():
            old_dj = detect_dir / "dataset.json"
            if old_dj.exists():
                try:
                    items = json.loads(old_dj.read_text(encoding="utf-8") or "[]")
                    dj.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
                except Exception as mig_err:
                    if logger:
                        logger.warning(f"Gagal migrasi dataset.json lama: {mig_err}")
                    dj.write_text("[]", encoding="utf-8")
            else:
                dj.write_text("[]", encoding="utf-8")
    except Exception as e:
        if logger:
            logger.error(f"ensure_detection_dirs error: {e}")

def save_detection_and_dataset(raw_bytes: bytes, label_norm: str, knn_conf: float | None, trash_pct: float, roi: tuple[int,int,int,int], logger: Any | None = None) -> dict:
    ensure_detection_dirs(logger)
    detect_dir = get_detection_dir()
    ensure_dir(detect_dir)
    ts = datetime.utcnow().isoformat(timespec="milliseconds") + "Z"
    short_id = uuid.uuid4().hex[:8]
    safe_label = label_norm.lower().replace(" ", "_")
    filename = f"{ts.replace(':','').replace('.','').replace('-','')}_{safe_label}_{short_id}.jpg"
    out_path = detect_dir / filename

    try:
        with open(out_path, "wb") as f:
            f.write(raw_bytes)
    except Exception as e:
        if logger:
            logger.error(f"Gagal menyimpan detection file: {e}")
        return {"ok": False, "error": str(e)}

    feats = {}
    try:
        bgr = decode_jpeg_to_bgr(raw_bytes)
        if bgr is not None:
            feats = extract_features_bgr(bgr)
    except Exception as e:
        if logger:
            logger.warning(f"Gagal ekstraksi fitur: {e}")

    try:
        dj = get_dataset_json()
        items = []
        if dj.exists():
            try:
                items = json.loads(dj.read_text(encoding="utf-8") or "[]")
            except Exception:
                items = []
        entry = {
            "path": str(out_path),
            "label": label_norm,
            "ts": ts,
            "features": feats,
            "knnConfidence": knn_conf,
            "trashPct": round(trash_pct, 2),
            "roi": {"x": roi[0], "y": roi[1], "w": roi[2], "h": roi[3]},
        }
        items.append(entry)
        dj.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"ok": True, "path": str(out_path), "entry": entry}
    except Exception as e:
        if logger:
            logger.error(f"Gagal update dataset.json: {e}")
        return {"ok": False, "error": str(e), "path": str(out_path)}