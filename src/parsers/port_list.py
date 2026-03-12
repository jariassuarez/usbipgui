import re

from models.client import AttachedPort

# Matches each in-use port block in `usbip port` output:
# Port 00: <Port in Use> at High Speed(480Mbps)
#        Vendor Name : Product Name (vid:pid)
#            -> usbip://192.168.1.1:3240/1-3
_PATTERN = re.compile(
    r"Port (\d+): <Port in Use> at (.+?)\n"
    r"\s+(.+?)\s+\((\w{4}):(\w{4})\)\s*\n"
    r"\s+->\s+usbip://([^:]+):\d+/(\S+)",
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
                remote_host=host.strip(),
                remote_busid=busid.strip(),
            )
        )
    return ports
