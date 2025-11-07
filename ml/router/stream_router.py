from fastapi import APIRouter
from fastapi.responses import StreamingResponse

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

@stream_router.get("/stream/html")
def stream_html():
    from fastapi.responses import HTMLResponse
    return HTMLResponse(
        """
        <!doctype html><html><head><meta charset="utf-8"><title>ML Stream</title>
          <style>
            body{margin:0;background:#111;height:100vh;color:#ddd;font-family:system-ui}
            .wrap{display:flex;align-items:center;justify-content:center;min-height:85vh}
            /* Full width dengan menjaga aspect ratio */
            img{width:98vw;height:auto;max-height:88vh;object-fit:contain;border:8px solid #333;border-radius:8px;box-shadow:0 10px 30px rgba(0,0,0,.5)}
            .toolbar{display:flex;gap:8px;align-items:center;justify-content:center;padding:10px}
            button{background:#444;color:#fff;border:none;padding:8px 12px;border-radius:6px;cursor:pointer}
            button.primary{background:#0a7}
            .badge{position:fixed;top:14px;left:14px;background:#222;color:#ddd;padding:6px 10px;border-radius:6px}
            .note{font-size:12px;color:#aaa;text-align:center;margin-top:6px}
          </style>
        </head>
        <body>
          <div class="badge">Stream Kamera</div>
          <div class="wrap"><img id="img" src="/stream" /></div>
          <div class="toolbar">
            <button id="startCam" class="primary">Mulai Kamera</button>
            <span id="dsInfo"></span>
          </div>
          <div class="note">Halaman melihat stream langsung dengan ukuran penuh.</div>
          <script>
            const dsInfo = document.getElementById('dsInfo');
            async function refreshStatus(){
              const st = await (await fetch('/status')).json();
              dsInfo.textContent = `open=${st.camera.open} backend=${st.camera.backend} src=${st.camera.src}`;
            }
            document.getElementById('startCam').onclick = async () => {
              await fetch('/camera', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({src:'0', backend:'AVFOUNDATION'})});
              await new Promise(r => setTimeout(r, 700));
              await refreshStatus();
            };
            refreshStatus();
          </script>
        </body></html>
        """
    )