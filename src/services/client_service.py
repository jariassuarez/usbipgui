import os

import parsers.port_list as port_list_parser
import parsers.remote_list as remote_list_parser
from models.client import AttachedPort, RemoteDevice
from services.executor import UsbipError, run


async def is_module_loaded() -> bool:
    return os.path.isdir("/sys/module/vhci_hcd")


async def load_module() -> None:
    if await is_module_loaded():
        return
    result = await run(["modprobe", "vhci-hcd"])
    if not result.ok:
        raise UsbipError(f"Failed to load vhci-hcd module: {result.stderr}")


async def list_remote(host: str) -> list[RemoteDevice]:
    result = await run(["usbip", "list", f"--remote={host}"])
    if not result.ok:
        raise UsbipError(f"Cannot reach {host}: {result.stderr}")
    devices = remote_list_parser.parse(result.stdout)
    if not devices:
        raise UsbipError(f"No exportable devices found on {host}")
    return devices


async def attach(host: str, busid: str) -> None:
    result = await run(["usbip", "attach", f"--remote={host}", f"--busid={busid}"])
    if not result.ok:
        raise UsbipError(f"Failed to attach {busid} from {host}: {result.stderr}")


async def detach(port: int) -> None:
    result = await run(["usbip", "detach", f"--port={port}"])
    if not result.ok:
        raise UsbipError(f"Failed to detach port {port}: {result.stderr}")


async def list_attached() -> list[AttachedPort]:
    result = await run(["usbip", "port"])
    if not result.ok:
        raise UsbipError(f"Failed to list attached ports: {result.stderr}")
    return port_list_parser.parse(result.stdout)
