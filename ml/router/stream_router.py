from fastapi import APIRouter
from fastapi.responses import StreamingResponse, HTMLResponse

stream_router = APIRouter()

@stream_router.get("/stream")
def stream():
    # Lazy import untuk hindari circular import
    from ml.app.service import mjpeg_from_latest, start_worker, _camera_status
    # Auto-start worker jika kamera belum terbuka
    try:
        st = dict(_camera_status)
        if not st.get("open"):
            start_worker()
    except Exception:
        pass
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Connection": "keep-alive",
    }
    return StreamingResponse(
        mjpeg_from_latest(),
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

@stream_router.get("/stream/html")
def stream_html():
    return HTMLResponse(
        """
        <!doctype html><html><head><meta charset="utf-8"><title>ML Stream</title>
          <style>
            body{margin:0;background:#111;height:100vh;color:#ddd;font-family:system-ui}
            .wrap{display:flex;align-items:center;justify-content:center;height:80vh}
            img{max-width:96vw;max-height:70vh;border:8px solid #333;border-radius:8px;box-shadow:0 10px 30px rgba(0,0,0,.5)}
            .toolbar{display:flex;gap:8px;align-items:center;justify-content:center;padding:10px}
            button{background:#444;color:#fff;border:none;padding:8px 12px;border-radius:6px;cursor:pointer}
            button.primary{background:#0a7}
            button.danger{background:#c33}
            .badge{position:fixed;top:14px;left:14px;background:#222;color:#ddd;padding:6px 10px;border-radius:6px}
            .note{font-size:12px;color:#aaa;text-align:center;margin-top:6px}
          </style>
        </head>
        <body>
          <div class="badge">Stream Kamera</div>
          <div class="wrap"><img id="img" src="/stream" /></div>
          <div class="toolbar">
            <button id="startCam" class="primary">Mulai Kamera</button>
            <button id="trainKnn">Train KNN</button>
            <span id="dsInfo"></span>
          </div>
          <div class="note">Halaman melihat stream langsung.</div>
          <script>
            const dsInfo = document.getElementById('dsInfo');
            async function refreshStatus(){
              const st = await (await fetch('/status')).json();
              const k = await (await fetch('/knn/status')).json();
              const ds = await (await fetch('/dataset/status')).json();
              dsInfo.textContent = `Camera open=${st.camera.open} • KNN loaded=${k.loaded} • Dataset: BERSIH=${ds.BERSIH} ADA_SAMPAH=${ds.ADA_SAMPAH} MENUMPUK=${ds.SAMPAH_MENUMPUK}`;
            }
            refreshStatus();
            document.getElementById('startCam').onclick = async () => {
              await fetch('/camera', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({src:'0', backend:'AVFOUNDATION'})});
              setTimeout(async () => {
                const st = await (await fetch('/status')).json();
                if (!st.camera.open) {
                  await fetch('/camera', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({src:'0', backend:'ANY'})});
                }
                refreshStatus();
              }, 600);
            };
            document.getElementById('trainKnn').onclick = async () => {
              const r = await fetch('/knn/train', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({}) });
              const j = await r.json();
              alert(j.ok ? `Model trained: ${j.modelPath}` : `Gagal training: ${j.error || 'unknown'}`);
              refreshStatus();
            };
          </script>
        </body></html>
        """
    )
