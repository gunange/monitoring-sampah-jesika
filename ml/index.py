from fastapi import FastAPI


# module: service.py (deklarasi global)
from ml.routers.camera_router import camera_router
from ml.routers.list_router import list_router

app = FastAPI()
app.include_router(camera_router)
app.include_router(list_router)