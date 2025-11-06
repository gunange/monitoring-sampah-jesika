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

LABEL_MAP = {"BERSIH": 0, "ADA_SAMPAH": 1}
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

def train_knn(
    labeled_root: Path = Path("ml/data/labeled"),
    out_path: Path = Path("ml/models/knn.joblib"),
    n_neighbors: int = 5,
) -> Path:
    X, y = [], []
    for img_path, lbl in iter_labeled_images(labeled_root):
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        X.append(extract_features(img))
        y.append(lbl)

    if not X:
        raise RuntimeError(f"Tidak ada data di {labeled_root}. Siapkan folder BERSIH/ADA_SAMPAH terlebih dahulu.")

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
    p_train.add_argument("--neighbors", type=int, default=5)
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