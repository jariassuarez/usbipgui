from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import services.client_service as svc

router = APIRouter(prefix="/client")
templates = Jinja2Templates(directory="templates")


@router.post("/module/load", response_class=HTMLResponse)
async def load_module(request: Request):
    try:
        await svc.load_module()
        module_loaded = True
        error = None
    except Exception as exc:
        module_loaded = False
        error = str(exc)
    return templates.TemplateResponse(
        "client/_vhci_status.html",
        {"request": request, "module_loaded": module_loaded, "error": error},
    )


@router.get("/list", response_class=HTMLResponse)
async def list_remote(request: Request, host: str):
    try:
        devices = await svc.list_remote(host)
        error = None
    except Exception as exc:
        devices = []
        error = str(exc)
    return templates.TemplateResponse(
        "client/_remote_devices.html",
        {"request": request, "host": host, "devices": devices, "error": error},
    )


@router.post("/attach", response_class=HTMLResponse)
async def attach(
    request: Request,
    host: str = Form(...),
    busid: str = Form(...),
):
    error = None
    try:
        await svc.attach(host, busid)
    except Exception as exc:
        error = str(exc)

    # Refresh remote device list after attach; device may no longer be listed
    # (it was just claimed), so don't treat an empty/failed refresh as an error
    try:
        devices = await svc.list_remote(host)
    except Exception:
        devices = []

    # Refresh attached ports for OOB swap
    try:
        attached = await svc.list_attached()
    except Exception:
        attached = []

    return templates.TemplateResponse(
        "client/_remote_devices.html",
        {
            "request": request,
            "host": host,
            "devices": devices,
            "attached": attached,
            "error": error,
            "oob_refresh_ports": True,
        },
    )


@router.post("/detach", response_class=HTMLResponse)
async def detach(request: Request, port: int = Form(...)):
    error = None
    try:
        await svc.detach(port)
    except Exception as exc:
        error = str(exc)

    try:
        attached = await svc.list_attached()
    except Exception as exc:
        attached = []
        error = error or str(exc)

    return templates.TemplateResponse(
        "client/_attached_ports.html",
        {"request": request, "attached": attached, "error": error},
    )


@router.get("/ports", response_class=HTMLResponse)
async def list_ports(request: Request):
    try:
        attached = await svc.list_attached()
        error = None
    except Exception as exc:
        attached = []
        error = str(exc)
    return templates.TemplateResponse(
        "client/_attached_ports.html",
        {"request": request, "attached": attached, "error": error},
    )
