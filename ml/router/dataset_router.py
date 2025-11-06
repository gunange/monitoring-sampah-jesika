from fastapi import APIRouter
from fastapi.responses import HTMLResponse

dataset_router = APIRouter()

@dataset_router.get("/dataset")
def dataset_html():
    return HTMLResponse(
        """
        <!doctype html><html><head><meta charset="utf-8"><title>Dataset Latih</title>
          <style>
            body{margin:0;background:#111;color:#ddd;font-family:system-ui}
            .wrap{display:flex;align-items:center;justify-content:center;height:72vh}
            img{max-width:96vw;max-height:66vh;border:8px solid #333;border-radius:8px;box-shadow:0 10px 30px rgba(0,0,0,.5)}
            .toolbar{display:flex;gap:10px;align-items:center;justify-content:center;padding:12px}
            button{background:#444;color:#fff;border:none;padding:8px 12px;border-radius:6px;cursor:pointer}
            button.primary{background:#0a7}
            button.danger{background:#c33}
            .badge{position:fixed;top:14px;left:14px;background:#222;color:#ddd;padding:6px 10px;border-radius:6px}
            .note{font-size:12px;color:#aaa;text-align:center;margin-top:6px}
          </style>
        </head>
        <body>
          <div class="badge">Dataset Latih</div>
          <div class="wrap">
            <div id="placeholder" style="width:85vw;height:60vh;background:#000;display:flex;align-items:center;justify-content:center;color:#ddd;border:8px solid #333;border-radius:8px;box-shadow:0 10px 30px rgba(0,0,0,.5)">Waiting for camera...</div>
            <img id="img" style="display:none" alt="camera" />
          </div>
          <div class="toolbar">
            <button id="startCam" class="primary">Mulai Kamera</button>
            <button id="saveBersih">Simpan BERSIH</button>
            <button id="saveSampah" class="danger">Simpan ADA SAMPAH</button>
            <span id="dsInfo"></span>
          </div>
          <div class="note">Jika stream gagal, halaman otomatis pakai fallback snapshot.</div>
          <script>
            const dsInfo = document.getElementById('dsInfo');
            const img = document.getElementById('img');
            const placeholder = document.getElementById('placeholder');

            function showImage() {
              img.style.display = '';
              placeholder.style.display = 'none';
            }

            async function refreshDataset() {
              const s = await (await fetch('/dataset/status')).json();
              dsInfo.textContent = `Dataset: BERSIH=${s.BERSIH} • ADA_SAMPAH=${s.ADA_SAMPAH}`;
            }
            refreshDataset();

            let usingRawFallback = false;
            let rawTimer = null;

            function attachStream() {
              usingRawFallback = false;
              if (rawTimer) { clearInterval(rawTimer); rawTimer = null; }
              img.src = '/stream?ts=' + Date.now();
              showImage();
            }

            function attachRawFallback() {
              if (usingRawFallback) return;
              usingRawFallback = true;
              img.src = '/frame/raw?ts=' + Date.now();
              showImage();
              if (rawTimer) clearInterval(rawTimer);
              rawTimer = setInterval(() => {
                img.src = '/frame/raw?ts=' + Date.now();
              }, 1000);
            }

            img.addEventListener('error', () => {
              attachRawFallback();
            });

            async function tryStartCamera() {
              attachRawFallback();
              await fetch('/camera', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({src:'0', backend:'AVFOUNDATION'})});
              await new Promise(r => setTimeout(r, 500));
              let st = await (await fetch('/status')).json();
              if (!st.camera || st.camera.open !== true) {
                await fetch('/camera', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({src:'0', backend:'ANY'})});
                await new Promise(r => setTimeout(r, 700));
                st = await (await fetch('/status')).json();
              }
              if (st.camera && st.camera.open === true) {
                attachStream();
              }
              refreshDataset();
            }

            document.getElementById('startCam').onclick = async () => {
              await tryStartCamera();
            };

            async function saveLabel(label) {
              const r = await fetch('/dataset/add', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({label})});
              const j = await r.json();
              alert(j.ok ? `Tersimpan: ${j.path}` : `Gagal: ${j.error || 'unknown'}`);
              refreshDataset();
            }
            document.getElementById('saveBersih').onclick = () => saveLabel('BERSIH');
            document.getElementById('saveSampah').onclick = () => saveLabel('ADA_SAMPAH');
          </script>
        </body></html>
        """
    )

@dataset_router.get("/dataset/status")
def dataset_status():
    # Lazy import untuk hindari circular import
    from ml.app.service import dataset_counts
    return dataset_counts()

@dataset_router.post("/dataset/add")
def dataset_add(payload: dict):
    # Lazy import untuk hindari circular import
    from pathlib import Path
    from ml.app.service import _state_lock, _latest_raw_jpeg, dataset_counts
    from ml.app.utils import ensure_dir, timestamp_str

    label = str(payload.get("label", "")).upper()
    if label not in {"BERSIH", "ADA_SAMPAH"}:
        return {"ok": False, "error": "Label harus BERSIH atau ADA_SAMPAH"}

    with _state_lock:
        raw_bytes = _latest_raw_jpeg
    if not raw_bytes:
        return {"ok": False, "error": "Belum ada frame mentah. Nyalakan kamera dan tunggu frame."}

    out_dir = Path("ml/data/labeled") / label
    ensure_dir(out_dir)
    fname = f"{label.lower()}_{timestamp_str()}.jpg"
    out_path = out_dir / fname
    try:
        with open(out_path, "wb") as f:
            f.write(raw_bytes)
    except Exception as e:
        return {"ok": False, "error": f"Gagal menyimpan: {e}"}

    counts = dataset_counts()
    return {"ok": True, "path": str(out_path), **counts}