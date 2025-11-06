from pathlib import Path
import csv
import random
import argparse

LABEL_DIRS = {
    "ADA_SAMPAH": Path("ml/data/labeled/ADA_SAMPAH"),
    "BERSIH": Path("ml/data/labeled/BERSIH"),
}

OUT_DIR = Path("ml/data/splits")

def collect_files() -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for label, d in LABEL_DIRS.items():
        if not d.exists():
            continue
        for p in sorted(d.glob("**/*")):
            if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"}:
                items.append((str(p), label))
    return items

def split_list(items: list[tuple[str, str]], ratios: tuple[float, float, float]):
    assert abs(sum(ratios) - 1.0) < 1e-6, "Rasio harus berjumlah 1.0"
    random.shuffle(items)
    n = len(items)
    n_train = int(n * ratios[0])
    n_val = int(n * ratios[1])
    train = items[:n_train]
    val = items[n_train:n_train+n_val]
    test = items[n_train+n_val:]
    return train, val, test

def write_csv(items: list[tuple[str, str]], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["path", "label"])
        for p, lbl in items:
            w.writerow([p, lbl])

def main(ratios=(0.7, 0.15, 0.15), seed: int = 42):
    random.seed(seed)
    items = collect_files()
    if not items:
        raise RuntimeError("Tidak ada file di ml/data/labeled/. Lakukan labeling terlebih dahulu.")
    train, val, test = split_list(items, ratios)
    write_csv(train, OUT_DIR / "train.csv")
    write_csv(val, OUT_DIR / "val.csv")
    write_csv(test, OUT_DIR / "test.csv")
    print(f"Selesai. train={len(train)} val={len(val)} test={len(test)} (total={len(items)})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Buat daftar train/val/test dari data/labeled.")
    parser.add_argument("--ratio", nargs=3, type=float, default=[0.7, 0.15, 0.15], help="Rasio train val test (jumlah=1.0)")
    parser.add_argument("--seed", type=int, default=42, help="Seed untuk shuffle")
    args = parser.parse_args()
    r = tuple(args.ratio)
    if abs(sum(r) - 1.0) > 1e-6:
        raise SystemExit("Rasio tidak valid, jumlah harus 1.0")
    main(ratios=r, seed=args.seed)