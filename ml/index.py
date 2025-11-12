from fastapi import FastAPI


# module: service.py (deklarasi global)
from ml.routers.camera_router import camera_router
from ml.routers.list_router import list_router
from ml.routers.machine_router import machine_router
from ml.routers.dataset_router import dataset_router

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from ml.app.logging import logger
from ml.services.main_service import machine_service

app = FastAPI()
# Global error handlers (bertindak seperti middleware untuk error)

@app.exception_handler(HTTPException)
async def handle_http_exception(request: Request, exc: HTTPException):
    detail = exc.detail if exc.detail else {"message": "HTTP error"}
    if not isinstance(detail, dict):
        detail = {"message": str(detail)}

    payload = {
        "error": detail,
        "path": request.url.path,
        "method": request.method,
    }
    logger.error(
        "HTTPException %s %s -> %s | detail=%s",
        request.method,
        request.url.path,
        exc.status_code,
        detail,
    )
    return JSONResponse(status_code=exc.status_code, content=payload)


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    payload = {
        "error": {"message": "Validation error", "details": errors},
        "path": request.url.path,
        "method": request.method,
    }
    logger.error(
        "ValidationError %s %s -> 422 | details=%s",
        request.method,
        request.url.path,
        errors,
    )
    return JSONResponse(status_code=422, content=payload)


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception):
    # logger.exception akan log stacktrace ke error.log
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    payload = {
        "error": {"message": "Internal server error"},
        "path": request.url.path,
        "method": request.method,
    }
    return JSONResponse(status_code=500, content=payload)

@app.on_event("startup")
def startup_event():
    machine_service.startup()

app.include_router(camera_router)
app.include_router(list_router)
app.include_router(machine_router)
app.include_router(dataset_router)
