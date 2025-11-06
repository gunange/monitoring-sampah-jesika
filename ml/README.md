# ML Service (Monitoring Sampah)

## Setup
1. `python3 -m venv ml/.venv && source ml/.venv/bin/activate`
2. `pip install -r ml/requirements.txt`
3. `cp ml/.env.example ml/.env` lalu sesuaikan isinya.

## Capture Data
- Jalankan: `python ml/app/capture.py`
- Gambar disimpan ke `ml/data/raw/`.

## Labeling
- Pindahkan gambar yang ada tumpukan sampah ke `ml/data/labeled/ADA_SAMPAH/`.
- Yang bersih ke `ml/data/labeled/BERSIH/`.

## Split Dataset
- Setelah labeling, jalankan: `python ml/app/splits.py --ratio 0.7 0.15 0.15`
- Hasil daftar `train.csv`, `val.csv`, `test.csv` di `ml/data/splits/`.