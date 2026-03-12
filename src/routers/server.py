from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

import services.server_service as svc
from config import settings

router = APIRouter(prefix="/server")
templates = Jinja2Templates(directory="templates")


@router.get("/status", response_class=HTMLResponse)
async def get_status(request: Request):
    try:
        status = await svc.get_status()
        error = None
    except Exception as exc:
        status = None
        error = str(exc)
    return templates.TemplateResponse(
        "server/_daemon_status.html",
        {"request": request, "status": status, "error": error},
    )


@router.post("/daemon/start")
async def start_daemon(request: Request):
    try:
        await svc.start(usbip_port=settings.usbip_port)
    except Exception:
        pass
    return RedirectResponse(url="/server/status", status_code=303)


@router.post("/daemon/stop")
async def stop_daemon(request: Request):
    try:
        await svc.stop()
    except Exception:
        pass
    return RedirectResponse(url="/server/status", status_code=303)


@router.get("/devices", response_class=HTMLResponse)
async def list_devices(request: Request):
    try:
        devices = await svc.list_devices()
        error = None
    except Exception as exc:
        devices = []
        error = str(exc)
    return templates.TemplateResponse(
        "server/_device_list.html",
        {"request": request, "devices": devices, "error": error},
    )


@router.post("/devices/{busid:path}/bind", response_class=HTMLResponse)
async def bind_device(busid: str, request: Request):
    error = None
    try:
        await svc.bind(busid)
    except Exception as exc:
        error = str(exc)

    try:
        devices = await svc.list_devices()
    except Exception as exc:
        devices = []
        error = error or str(exc)

    return templates.TemplateResponse(
        "server/_device_list.html",
        {"request": request, "devices": devices, "error": error},
    )


@router.post("/devices/{busid:path}/unbind", response_class=HTMLResponse)
async def unbind_device(busid: str, request: Request):
    error = None
    try:
        await svc.unbind(busid)
    except Exception as exc:
        error = str(exc)

    try:
        devices = await svc.list_devices()
    except Exception as exc:
        devices = []
        error = error or str(exc)

    return templates.TemplateResponse(
        "server/_device_list.html",
        {"request": request, "devices": devices, "error": error},
    )
