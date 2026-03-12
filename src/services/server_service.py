import os
import re

import parsers.local_list as local_list_parser
from models.server import DaemonStatus, LocalDevice
from services.executor import UsbipError, run


async def get_status() -> DaemonStatus:
    module_loaded = _is_module_loaded()
    pid = await _find_daemon_pid()
    return DaemonStatus(
        host_module_loaded=module_loaded,
        is_running=pid is not None,
        pid=pid,
    )


async def start(usbip_port: int = 3240) -> DaemonStatus:
    if not _is_module_loaded():
        result = await run(["modprobe", "usbip_host"])
        if not result.ok:
            raise UsbipError(f"Failed to load usbip_host module: {result.stderr}")

    pid = await _find_daemon_pid()
    if pid is None:
        result = await run(["usbipd", f"--tcp-port={usbip_port}"])
        if not result.ok:
            # usbipd may exit immediately after forking into daemon mode; ignore rc 0 or fork
            pass
        pid = await _find_daemon_pid()

    return DaemonStatus(
        host_module_loaded=_is_module_loaded(),
        is_running=pid is not None,
        pid=pid,
    )


async def stop() -> DaemonStatus:
    result = await run(["pkill", "-x", "usbipd"])
    if not result.ok and result.returncode != 1:
        # pkill returns 1 when no process matched, which is harmless
        raise UsbipError(f"Failed to stop usbipd: {result.stderr}")
    return DaemonStatus(
        host_module_loaded=_is_module_loaded(),
        is_running=False,
        pid=None,
    )


async def list_devices() -> list[LocalDevice]:
    result = await run(["usbip", "list", "--local"])
    if not result.ok:
        raise UsbipError(f"Failed to list USB devices: {result.stderr}")

    devices = local_list_parser.parse(result.stdout)
    exported = _exported_busids()
    for device in devices:
        device.is_exported = device.busid in exported
    return devices


async def bind(busid: str) -> None:
    result = await run(["usbip", "bind", f"--busid={busid}"])
    if not result.ok:
        raise UsbipError(f"Failed to bind {busid}: {result.stderr}")


async def unbind(busid: str) -> None:
    result = await run(["usbip", "unbind", f"--busid={busid}"])
    if not result.ok:
        raise UsbipError(f"Failed to unbind {busid}: {result.stderr}")


def _is_module_loaded() -> bool:
    return os.path.isdir("/sys/module/usbip_host")


def _exported_busids() -> set[str]:
    """Read exported busids from sysfs without spawning a subprocess."""
    path = "/sys/bus/usb/drivers/usbip-host"
    if not os.path.isdir(path):
        return set()
    return {
        entry
        for entry in os.listdir(path)
        if re.match(r"^\d+-\d+", entry)
    }


async def _find_daemon_pid() -> int | None:
    result = await run(["pgrep", "-x", "usbipd"])
    if result.ok and result.stdout.isdigit():
        return int(result.stdout)
    return None
