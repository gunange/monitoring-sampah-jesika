import json
from pathlib import Path
from typing import Tuple, List, Optional

import numpy as np
import cv2

from ml.app.utils import get_logger
from ml.app.knn import extract_features as _knn_extract

logger = get_logger("reference", Path("ml/logs/ml_service.log"))

_REF_FEATS: Optional[np.ndarray] = None
_REF_LABELS: List[str] = []
_REF_COUNT = {"BERSIH": 0, "ADA SAMPAH": 0, "TOTAL": 0}

def _vector_from_features_dict(fd: dict) -> Optional[np.ndarray]:
    try:
        h = np.asarray(fd.get("color_hist_h", []), dtype=np.float32)
        s = np.asarray(fd.get("color_hist_s", []), dtype=np.float32)
        v = np.asarray(fd.get("color_hist_v", []), dtype=np.float32)
        if h.size != 16 or s.size != 16 or v.size != 16:
            # Tidak konsisten → abaikan entri ini
            return None
        # L1 normalisasi defensif
        def l1(x: np.ndarray) -> np.ndarray:
            s = float(x.sum()) or 1.0
            return (x / s).astype(np.float32)
        h = l1(h); s = l1(s); v = l1(v)

        edge_density = float(fd.get("edge_ratio", 0.0))
        lap_var = float(fd.get("laplacian_var", 0.0))
        v_mean = float(fd.get("v_mean", 0.0)) / 255.0 if fd.get("v_mean") is not None else 0.0
        v_std  = float(fd.get("v_std", 0.0)) / 255.0 if fd.get("v_std") is not None else 0.0

        vec = np.concatenate([h, s, v, np.array([edge_density, lap_var, v_mean, v_std], dtype=np.float32)])
        return vec.astype(np.float32)
    except Exception as e:
        logger.warning(f"_vector_from_features_dict error: {e}")
        return None

def load_reference_dataset(path: Path = Path("ml/data/dataset.json")) -> dict:
    global _REF_FEATS, _REF_LABELS, _REF_COUNT
    _REF_FEATS, _REF_LABELS = None, []
    _REF_COUNT = {"BERSIH": 0, "ADA SAMPAH": 0, "TOTAL": 0}
    if not path.exists():
        logger.info(f"Dataset referensi tidak ditemukan: {path}")
        return {"ok": False, "count": 0}

    try:
        items = json.loads(path.read_text(encoding="utf-8") or "[]")
    except Exception as e:
        logger.error(f"Gagal membaca dataset.json: {e}")
        return {"ok": False, "count": 0, "error": str(e)}

    feats = []
    labels = []
    for it in items:
        fd = (it.get("features") or {})
        lbl = str(it.get("label") or "").strip()
        vec = _vector_from_features_dict(fd)
        if vec is None:
            continue
        feats.append(vec)
        labels.append(lbl)
        if lbl.upper().replace("_", " ") == "ADA SAMPAH":
            _REF_COUNT["ADA SAMPAH"] += 1
        elif lbl.upper() == "BERSIH":
            _REF_COUNT["BERSIH"] += 1

    if feats:
        _REF_FEATS = np.vstack(feats).astype(np.float32)
        _REF_LABELS = labels
        _REF_COUNT["TOTAL"] = len(labels)
        logger.info(f"Referensi dimuat: TOTAL={_REF_COUNT['TOTAL']} BERSIH={_REF_COUNT['BERSIH']} ADA SAMPAH={_REF_COUNT['ADA SAMPAH']}")
        return {"ok": True, "count": _REF_COUNT["TOTAL"], "stats": dict(_REF_COUNT)}
    else:
        logger.info("Dataset referensi kosong atau tidak valid.")
        return {"ok": False, "count": 0}

def has_reference() -> bool:
    return _REF_FEATS is not None and len(_REF_LABELS) > 0

def _cosine_sim_matrix(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    # sim(A_i, b) = (A_i · b) / (||A_i|| * ||b||)
    A_norm = np.linalg.norm(A, axis=1) + 1e-8
    b_norm = float(np.linalg.norm(b)) + 1e-8
    dots = A @ b
    return dots / (A_norm * b_norm)

def compute_similarity(img_bgr: np.ndarray, knn_model: Optional[object] = None, topk: int = 5) -> Tuple[Optional[str], float, float]:
    """
    Mengembalikan: (label_top1, skor_top1, rata2_topk)
    """
    if not has_reference():
        return None, 0.0, 0.0

    # Ekstraksi fitur konsisten KNN
    vec = _knn_extract(img_bgr).astype(np.float32)

    # Jika ada scaler di pipeline, transform di ruang yang sama
    A = _REF_FEATS
    if knn_model is not None:
        try:
            scaler = knn_model.named_steps.get("scaler")
            if scaler is not None:
                A = scaler.transform(A)
                vec = scaler.transform([vec])[0]
        except Exception:
            pass

    sims = _cosine_sim_matrix(A, vec)
    idx = int(np.argmax(sims))
    top1_label = _REF_LABELS[idx]
    top1_score = float(sims[idx])

    k = int(min(topk, sims.size))
    if k > 1:
        order = np.argsort(-sims)[:k]
        avg_topk = float(np.mean(sims[order]))
    else:
        avg_topk = top1_score

    return top1_label, top1_score, avg_topk