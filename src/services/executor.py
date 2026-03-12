import asyncio
from dataclasses import dataclass

from config import settings

# Commands that do not need sudo even when use_sudo is enabled
# Note: pgrep is read-only and doesn't need sudo
# pkill MUST use sudo to kill system processes, so it's removed from this list
_NO_SUDO = frozenset({"pgrep", "lsmod", "cat", "ls"})


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


class UsbipError(Exception):
    pass


async def run(cmd: list[str], timeout: float = 30.0) -> CommandResult:
    effective = cmd
    if settings.use_sudo and cmd[0] not in _NO_SUDO:
        effective = ["sudo", "-n"] + cmd

    try:
        proc = await asyncio.create_subprocess_exec(
            *effective,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return CommandResult(
            returncode=proc.returncode,
            stdout=stdout.decode(errors="replace").strip(),
            stderr=stderr.decode(errors="replace").strip(),
        )
    except asyncio.TimeoutError:
        raise UsbipError(f"Command timed out after {timeout}s: {' '.join(effective)}")
    except FileNotFoundError as exc:
        raise UsbipError(f"Executable not found: {exc}")
