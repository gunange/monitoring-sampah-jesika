# Fungsi: dataset_html, dataset_add, dan endpoint baru dataset_capture_upload

from fastapi import APIRouter, Request
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
            .toolbar{display:flex;gap:10px;align-items:center;justify-content:center;padding:12px;flex-wrap:wrap}
            button{background:#444;color:#fff;border:none;padding:8px 12px;border-radius:6px;cursor:pointer}
            button.primary{background:#0a7}
            button.danger{background:#c33}
            input[type=file]{color:#ddd}
            select{background:#222;color:#ddd;border:1px solid #333;padding:6px;border-radius:6px}
            .badge{position:fixed;top:14px;left:14px;background:#222;color:#ddd;padding:6px 10px;border-radius:6px}
            .note{font-size:12px;color:#aaa;text-align:center;margin-top:6px}
            .status{font-size:12px;color:#aaa;text-align:center;margin-top:6px;white-space:pre-line}
          </style>
        </head>
        <body>
          <div class="badge">Dataset Latih</div>
          <div class="wrap">
            <div id="placeholder" style="width:100vw;height:70vh;background:#000;display:flex;align-items:center;justify-content:center;color:#ddd;border:8px solid #333;border-radius:8px;box-shadow:0 10px 30px rgba(0,0,0,.5)">Waiting for camera...</div>
            <img id="img" style="display:none" alt="preview" />
          </div>
          <div class="toolbar">
            <button id="startCam" class="primary">Mulai Kamera</button>
            <button id="showStatus">Status Kamera</button>
            <button id="saveBersih">Simpan BERSIH</button>
            <button id="saveSampah" class="danger">Simpan ADA SAMPAH</button>
            <input type="file" id="uploadFile" accept="image/*" />
            <select id="uploadLabel">
              <option value="BERSIH">BERSIH</option>
              <option value="ADA SAMPAH">ADA SAMPAH</option>
            </select>
            <button id="uploadBtn">Upload</button>
            <span id="dsInfo"></span>
          </div>
          <div class="note">Jika stream gagal, halaman otomatis pakai fallback snapshot. Anda juga bisa unggah file gambar yang sudah ada.</div>
          <div id="camStatus" class="status"></div>
          <script>
            const dsInfo = document.getElementById('dsInfo');
            const img = document.getElementById('img');
            const placeholder = document.getElementById('placeholder');
            const camStatus = document.getElementById('camStatus');

            function showImage() {
              img.style.display = '';
              placeholder.style.display = 'none';
            }
            function showPlaceholder() {
              img.style.display = 'none';
              placeholder.style.display = 'flex';
            }

            async function refreshDataset() {
              const s = await (await fetch('/dataset/status')).json();
              dsInfo.textContent = `Dataset: BERSIH=${s.BERSIH} • ADA_SAMPAH=${s.ADA_SAMPAH}`;
            }
            refreshDataset();

            let usingRawFallback = false;
            let rawTimer = null;

            // Tanpa polling: perbarui tombol hanya saat diperlukan
            async function updateCamButton() {
              try {
                const st = await (await fetch('/status')).json();
                const btn = document.getElementById('startCam');
                if (st.camera && st.camera.open === true) {
                  btn.textContent = 'Stop Service';
                  btn.classList.remove('primary');
                  btn.classList.add('danger');
                } else {
                  btn.textContent = 'Mulai Kamera';
                  btn.classList.remove('danger');
                  btn.classList.add('primary');
                  showPlaceholder();
                }
              } catch(e) {}
            }

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

            async function showCamStatus() {
              const st = await (await fetch('/status')).json();
              const diag = await (await fetch('/diag/camera')).json();
              const lines = [];
              lines.push(`open=${st.camera.open} backend=${st.camera.backend} src=${st.camera.src} saveDetections=${st.camera.saveDetections}`);
              if (st.camera.last_error) lines.push(`last_error=${st.camera.last_error}`);
              lines.push('diagnostic:');
              diag.results.forEach(r => lines.push(`- ${r.backend} opened=${r.opened} read_ok=${r.read_ok} error=${r.error || '-'}`));
              camStatus.textContent = lines.join('\\n');
            }

            async function tryStartCamera() {
              // Start seluruh service (worker + scheduler)
              attachRawFallback();
              await fetch('/machine/start', {method:'GET'});
              await new Promise(r => setTimeout(r, 900));
              await showCamStatus();
              const st = await (await fetch('/status')).json();
              if (st.camera && st.camera.open === true) {
                attachStream();
              }
              await updateCamButton(); // update tombol sekali
              refreshDataset();
            }

            async function stopService() {
              await fetch('/machine/stop', {method:'GET'});
              if (rawTimer) { clearInterval(rawTimer); rawTimer = null; }
              showPlaceholder();
              await showCamStatus();
              await updateCamButton(); // sekali saja
            }

            document.getElementById('startCam').onclick = async () => {
              const st = await (await fetch('/status')).json();
              if (st.camera && st.camera.open === true) {
                await stopService();
              } else {
                await tryStartCamera();
              }
            };
            document.getElementById('showStatus').onclick = async () => {
              await showCamStatus();
              await updateCamButton();
            };

            // Inisialisasi satu kali tanpa polling
            updateCamButton();

            // Upload & Simpan tetap sama
            document.getElementById('saveBersih').onclick = async () => {
              const r = await fetch('/dataset/add', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({label:'BERSIH'})});
              const j = await r.json();
              alert(j.ok ? `Tersimpan: ${j.path}` : `Gagal: ${j.error || 'unknown'}`);
              refreshDataset();
            };
            document.getElementById('saveSampah').onclick = async () => {
              const r = await fetch('/dataset/add', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({label:'ADA_SAMPAH'})});
              const j = await r.json();
              alert(j.ok ? `Tersimpan: ${j.path}` : `Gagal: ${j.error || 'unknown'}`);
              refreshDataset();
            };
            document.getElementById('uploadFile').addEventListener('change', async (e) => {
              const file = e.target.files[0];
              if (!file) return;
              img.src = URL.createObjectURL(file);
              showImage();
              await fetch('/dataset/capture/upload', {
                method: 'POST',
                headers: { 'Content-Type': file.type || 'application/octet-stream' },
                body: file
              });
            });
            document.getElementById('uploadBtn').onclick = async () => {
              const file = document.getElementById('uploadFile').files[0];
              if (!file) { alert('Pilih file dulu'); return; }
              const label = document.getElementById('uploadLabel').value;
              const r = await fetch('/dataset/upload?label=' + encodeURIComponent(label), {
                method: 'POST',
                headers: { 'Content-Type': file.type || 'application/octet-stream' },
                body: file
              });
              const j = await r.json();
              alert(j.ok ? `Tersimpan: ${j.path}` : `Gagal: ${j.error || 'unknown'}`);
              refreshDataset();
            };
          </script>
        </body></html>
        """
    )

@dataset_router.get("/dataset/status")
def dataset_status():
    # Lazy import untuk hindari circular import
    from ml.app.service import dataset_counts
    return dataset_counts()

@dataset_router.post("/dataset/capture/upload")
async def dataset_capture_upload(request: Request):
    import ml.app.service as svc
    from ml.app.service import _state_lock

    try:
        file_bytes = await request.body()
    except Exception as e:
        return {"ok": False, "error": f"Gagal membaca body: {e}"}
    if not file_bytes:
        return {"ok": False, "error": "Body kosong; kirim gambar sebagai biner."}

    with _state_lock:
        svc._captured_raw_jpeg = file_bytes
    return {"ok": True, "size": len(file_bytes)}

@dataset_router.post("/dataset/add")
def dataset_add(payload: dict):
    # Lazy import untuk hindari circular import
    from pathlib import Path
    import ml.app.service as svc
    from ml.app.service import _state_lock, dataset_counts
    from ml.app.utils import ensure_dir, timestamp_str

    label = str(payload.get("label", "")).upper()
    # Samakan normalisasi label seperti upload
    if label in {"CLEAN", "BERSIH"}:
        norm_label = "BERSIH"
    elif label in {"TRASH", "ADA SAMPAH", "ADA_SAMPAH", "SAMPAH"}:
        norm_label = "ADA SAMPAH"
    else:
        return {"ok": False, "error": "Label harus BERSIH atau ADA SAMPAH"}

    with _state_lock:
        raw_bytes = getattr(svc, "_captured_raw_jpeg", None) or getattr(svc, "_latest_raw_jpeg", None)

    if not raw_bytes:
        return {"ok": False, "error": "Belum ada frame mentah. Ambil gambar, nyalakan kamera, atau pilih file."}

    from ml.app.service import get_detection_dir
    out_dir = get_detection_dir()
    ensure_dir(out_dir)
    # Format nama file diselaraskan dengan upload
    from datetime import datetime
    import uuid
    ts = datetime.utcnow().isoformat(timespec="milliseconds") + "Z"
    short_id = uuid.uuid4().hex[:8]
    safe_label = norm_label.lower().replace(" ", "_")
    fname = f"{ts.replace(':','').replace('.','').replace('-','')}_{safe_label}_{short_id}.jpg"
    out_path = out_dir / fname
    try:
        with open(out_path, "wb") as f:
            f.write(raw_bytes)
    except Exception as e:
        return {"ok": False, "error": f"Gagal menyimpan: {e}"}

    counts = dataset_counts()
    return {"ok": True, "path": str(out_path), **counts}

@dataset_router.post("/dataset/upload")
async def dataset_upload(request: Request, label: str = ""):
    from pathlib import Path
    import uuid, json
    from datetime import datetime
    from ml.app.utils import ensure_dir
    from ml.app.service import (
        ensure_detection_dirs,
        get_detection_dir,
        get_dataset_json,
        decode_jpeg_to_bgr,
        extract_features_bgr,
        dataset_counts,
        logger,
    )

    ensure_detection_dirs()

    raw_label = (label or "").strip().upper()
    if raw_label in {"CLEAN", "BERSIH"}:
        norm_label = "BERSIH"
    elif raw_label in {"TRASH", "ADA SAMPAH", "ADA_SAMPAH", "SAMPAH"}:
        norm_label = "ADA SAMPAH"
    else:
        return {"ok": False, "error": "Label harus BERSIH atau ADA SAMPAH"}

    try:
        file_bytes = await request.body()
    except Exception as e:
        return {"ok": False, "error": f"Gagal membaca body: {e}"}
    if not file_bytes:
        return {"ok": False, "error": "Body kosong; kirim gambar sebagai biner."}

    ct = (request.headers.get("content-type") or "").lower()
    ext = ".jpg"
    if ct.startswith("image/"):
        if "jpeg" in ct or "jpg" in ct:
            ext = ".jpg"
        elif "png" in ct:
            ext = ".png"
        elif "bmp" in ct:
            ext = ".bmp"
        elif "webp" in ct:
            ext = ".webp"
    elif ct == "application/octet-stream":
        ext = ".jpg"

    detect_dir = get_detection_dir()
    ensure_dir(detect_dir)
    ts = datetime.utcnow().isoformat(timespec="milliseconds") + "Z"
    short_id = uuid.uuid4().hex[:8]
    safe_label = norm_label.lower().replace(" ", "_")
    filename = f"{ts.replace(':','').replace('.','').replace('-','')}_{safe_label}_{short_id}{ext}"
    out_path = detect_dir / filename

    try:
        with open(out_path, "wb") as f:
            f.write(file_bytes)
    except Exception as e:
        return {"ok": False, "error": f"Gagal menyimpan file: {e}"}

    feats = {}
    try:
        try:
            bgr = decode_jpeg_to_bgr(file_bytes)
        except Exception:
            import numpy as _np, cv2 as _cv
            bgr = _cv.imdecode(_np.frombuffer(file_bytes, dtype=_np.uint8), _cv.IMREAD_COLOR)
        if bgr is not None:
            feats = extract_features_bgr(bgr)
    except Exception as e:
        logger.warning(f"Gagal ekstraksi fitur: {e}")

    entry = {"path": str(out_path), "label": norm_label, "ts": ts, "features": feats}

    try:
        dj = get_dataset_json()
        items = []
        if dj.exists():
            items = json.loads(dj.read_text(encoding="utf-8") or "[]")
        items.append(entry)
        dj.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        return {"ok": False, "error": f"Gagal update dataset.json: {e}", "path": str(out_path), "entry": entry}

    return {"ok": True, "path": str(out_path), "entry": entry, **dataset_counts()}