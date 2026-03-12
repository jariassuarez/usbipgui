from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import services.client_service as client_svc
import services.server_service as server_svc

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/server", response_class=HTMLResponse)
async def server_page(request: Request):
    try:
        status = await server_svc.get_status()
        devices = await server_svc.list_devices() if status.host_module_loaded else []
        error = None
    except Exception as exc:
        status = None
        devices = []
        error = str(exc)
    return templates.TemplateResponse(
        "server/page.html",
        {"request": request, "status": status, "devices": devices, "error": error},
    )


@router.get("/client", response_class=HTMLResponse)
async def client_page(request: Request):
    try:
        module_loaded = await client_svc.is_module_loaded()
        attached = await client_svc.list_attached() if module_loaded else []
        error = None
    except Exception as exc:
        module_loaded = False
        attached = []
        error = str(exc)
    return templates.TemplateResponse(
        "client/page.html",
        {
            "request": request,
            "module_loaded": module_loaded,
            "attached": attached,
            "error": error,
        },
    )
