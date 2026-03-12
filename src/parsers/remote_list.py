import re

from models.client import RemoteDevice

# Matches device lines in `usbip list --remote=HOST` output:
#    1-3: Primax Electronics, Ltd : Dell Mouse (0461:4e22)
_PATTERN = re.compile(
    r"^\s+([\d][\d.\-]+):\s+(.+?)\s+\((\w{4}):(\w{4})\)\s*$",
    re.MULTILINE,
)


def parse(output: str) -> list[RemoteDevice]:
    devices: list[RemoteDevice] = []
    for match in _PATTERN.finditer(output):
        busid, description, vendor_id, product_id = match.groups()
        vendor_name, _, product_name = description.partition(" : ")
        devices.append(
            RemoteDevice(
                busid=busid.strip(),
                busid_safe=busid.strip().replace(".", "-"),
                vendor_id=vendor_id,
                product_id=product_id,
                vendor_name=vendor_name.strip() or "Unknown",
                product_name=product_name.strip() or "Unknown",
            )
        )
    return devices
