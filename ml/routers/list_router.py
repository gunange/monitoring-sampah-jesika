from fastapi import APIRouter, Request
from fastapi.routing import APIRoute

list_router = APIRouter()

@list_router.get("/routes")
def list_routes(request: Request):
    routes = []
    for r in request.app.routes:
        if isinstance(r, APIRoute):
            routes.append({
                "path": r.path,
                "methods": sorted(list(r.methods or [])),
                "name": r.name,
            })
    return {"count": len(routes), "routes": routes}