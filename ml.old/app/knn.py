# module: knn.py
from __future__ import annotations
from pathlib import Path
import argparse, json
import cv2, numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
import joblib
from typing import Iterable, Tuple
from .config import get_int  # baca env untuk KNN_NEIGHBORS

# kelas/fungsi terkait
# Top-level constants
LABEL_MAP = {"BERSIH": 0, "ADA_SAMPAH": 1, "SAMPAH_MENUMPUK": 2}
INV_LABEL_MAP = {v: k for k, v in LABEL_MAP.items()}

def extract_features(img_bgr: np.ndarray) -> np.ndarray:
    # Resize ringan agar fitur konsisten
    img = cv2.resize(img_bgr, (128, 128), interpolation=cv2.INTER_AREA)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Histogram HSV (warna)
    h_hist = cv2.calcHist([hsv], [0], None, [16], [0, 180]).flatten()
    s_hist = cv2.calcHist([hsv], [1], None, [16], [0, 256]).flatten()
    v_hist = cv2.calcHist([hsv], [2], None, [16], [0, 256]).flatten()
    h_hist = (h_hist / (h_hist.sum() + 1e-6)).astype(np.float32)
    s_hist = (s_hist / (s_hist.sum() + 1e-6)).astype(np.float32)
    v_hist = (v_hist / (v_hist.sum() + 1e-6)).astype(np.float32)

    # Tekstur sederhana: kerapatan tepi + variansi Laplacian
    edges = cv2.Canny(gray, 100, 200)
    edge_density = float(edges.mean() / 255.0)
    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    # Statistik intensitas (mean/std V)
    v_mean = float(np.mean(hsv[:, :, 2])) / 255.0
    v_std = float(np.std(hsv[:, :, 2])) / 255.0

    feats = np.concatenate(
        [h_hist, s_hist, v_hist, np.array([edge_density, lap_var, v_mean, v_std], dtype=np.float32)]
    )
    return feats.astype(np.float32)

def iter_labeled_images(root: Path) -> Iterable[Tuple[Path, int]]:
    for name, lbl in LABEL_MAP.items():
        d = root / name
        if not d.exists():
            continue
        for p in sorted(d.glob("**/*")):
            if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"}:
                yield p, lbl

# === BARU: bangun vektor dari dataset.json ===
def _vector_from_features_dict(fd: dict) -> np.ndarray | None:
    try:
        import numpy as np
        h = np.asarray(fd.get("color_hist_h", []), dtype=np.float32)
        s = np.asarray(fd.get("color_hist_s", []), dtype=np.float32)
        v = np.asarray(fd.get("color_hist_v", []), dtype=np.float32)
        if h.size != 16 or s.size != 16 or v.size != 16:
            return None
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
    except Exception:
        return None

def train_knn(
    labeled_root: Path = Path("ml/data/labeled"),
    out_path: Path = Path("ml/models/knn.joblib"),
    n_neighbors: int | None = None,
) -> Path:
    X, y = [], []
    for img_path, lbl in iter_labeled_images(labeled_root):
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        X.append(extract_features(img))
        y.append(lbl)

    if not X:
        raise RuntimeError(f"Tidak ada data di {labeled_root}. Siapkan folder BERSIH/ADA_SAMPAH/SAMPAH_MENUMPUK terlebih dahulu.")
    # Ambil K dari .env jika tidak diberikan
    n_neighbors = int(n_neighbors if n_neighbors is not None else get_int("KNN_NEIGHBORS", 5))
    X = np.asarray(X, dtype=np.float32)
    y = np.asarray(y, dtype=np.int32)
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("knn", KNeighborsClassifier(n_neighbors=n_neighbors, weights="distance")),
    ])
    model.fit(X, y)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out_path)
    return out_path

# === BARU: latih KNN dari dataset.json (versi terbaru sistem) ===
def train_knn_from_dataset_json(
    dataset_path: Path = Path("ml/data/dataset.json"),
    out_path: Path = Path("ml/models/knn.joblib"),
    n_neighbors: int | None = None,
) -> Path:
    import json, numpy as np
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.neighbors import KNeighborsClassifier
    import joblib

    items = []
    if dataset_path.exists():
        items = json.loads(dataset_path.read_text(encoding="utf-8") or "[]")

    X, y = [], []
    for it in items:
        fd = it.get("features") or {}
        vec = _vector_from_features_dict(fd)
        lbl_raw = str(it.get("label") or "").strip().upper().replace(" ", "_")
        if vec is None:
            continue
        if lbl_raw not in LABEL_MAP:
            continue
        X.append(vec); y.append(LABEL_MAP[lbl_raw])

    if not X:
        raise RuntimeError("Dataset kosong/tidak valid di ml/data/dataset.json")
    # Ambil K dari .env jika tidak diberikan
    n_neighbors = int(n_neighbors if n_neighbors is not None else get_int("KNN_NEIGHBORS", 5))
    X = np.asarray(X, dtype=np.float32)
    y = np.asarray(y, dtype=np.int32)
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("knn", KNeighborsClassifier(n_neighbors=n_neighbors, weights="distance")),
    ])
    model.fit(X, y)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out_path)
    return out_path

def load_knn(model_path: Path) -> Pipeline | None:
    if not model_path.exists():
        return None
    return joblib.load(model_path)

def predict_knn(model: Pipeline, img_bgr: np.ndarray) -> tuple[str, float]:
    feats = extract_features(img_bgr)
    probs = model.predict_proba([feats])[0]
    label_idx = int(np.argmax(probs))
    label = INV_LABEL_MAP[label_idx]
    conf = float(probs[label_idx])
    return label, conf

def build_dataset_json(
    labeled_root: Path = Path("ml/data/labeled"),
    out_json: Path = Path("ml/data/dataset.json"),
) -> Path:
    rows = []
    for p, lbl in iter_labeled_images(labeled_root):
        img = cv2.imread(str(p))
        if img is None:
            continue
        feats = extract_features(img).tolist()
        rows.append({"path": str(p), "label": INV_LABEL_MAP[lbl], "features": feats})
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(rows, indent=2))
    return out_json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KNN tools: train model atau ekspor dataset JSON.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_train = sub.add_parser("train", help="Latih KNN dari ml/data/labeled")
    p_train.add_argument("--neighbors", type=int, default=get_int("KNN_NEIGHBORS", 5))
    p_train.add_argument("--out", type=Path, default=Path("ml/models/knn.joblib"))
    p_train.add_argument("--root", type=Path, default=Path("ml/data/labeled"))

    p_export = sub.add_parser("export-json", help="Ekspor dataset fitur ke JSON")
    p_export.add_argument("--out", type=Path, default=Path("ml/data/dataset.json"))
    p_export.add_argument("--root", type=Path, default=Path("ml/data/labeled"))

    args = parser.parse_args()
    if args.cmd == "train":
        out = train_knn(labeled_root=args.root, out_path=args.out, n_neighbors=args.neighbors)
        print(f"Model tersimpan: {out}")
    elif args.cmd == "export-json":
        out = build_dataset_json(labeled_root=args.root, out_json=args.out)
        print(f"Dataset JSON: {out}")