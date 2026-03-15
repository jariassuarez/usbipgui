import re

from models.client import AttachedPort

# Matches each in-use port block in `usbip port` output.
#
# Normal format (local busid prefix before usbip://):
#   Port 00: <Port in Use> at Full Speed(12Mbps)
#          Vendor Name : Product Name (vid:pid)
#          8-1 -> usbip://192.168.1.1:3240/1-3
#              -> remote bus/dev 001/004
#
# Degraded format (libusbip: error: fopen / read_record — record files missing):
#   Port 00: <Port in Use> at Full Speed(12Mbps)
#          Vendor Name : Product Name (vid:pid)
#          8-1 -> unknown host, remote port and remote busid
#              -> remote bus/dev 001/004
_PATTERN = re.compile(
    r"Port (\d+): <Port in Use> at (.+?)\n"
    r"\s+(.+?)\s+\((\w{4}):(\w{4})\)\s*\n"
    r"(?:"
    r"\s+(?:\S+\s+)?->\s+usbip://([^:]+):\d+/(\S+)"   # normal: optional busid prefix, captures host + busid
    r"|"
    r"\s+\S+\s+->\s+unknown host[^\n]*"                # degraded: no host/busid available
    r")",
    re.MULTILINE,
)


def parse(output: str) -> list[AttachedPort]:
    ports: list[AttachedPort] = []
    for match in _PATTERN.finditer(output):
        port, speed, description, vendor_id, product_id, host, busid = match.groups()
        ports.append(
            AttachedPort(
                port=int(port),
                speed=speed.strip(),
                vendor_id=vendor_id,
                product_id=product_id,
                remote_host=(host or "unknown").strip(),
                remote_busid=(busid or "unknown").strip(),
            )
        )
    return ports
