import re

from models.server import LocalDevice

# Matches the two-line block per device in `usbip list --local` output:
#  - busid 1-3 (0461:4e22)
#    Primax Electronics, Ltd : Dell Mouse (0461:4e22)
_PATTERN = re.compile(
    r"^\s*-\s+busid\s+(\S+)\s+\((\w{4}):(\w{4})\)\s*\n\s+(.+)$",
    re.MULTILINE,
)


def parse(output: str) -> list[LocalDevice]:
    devices: list[LocalDevice] = []
    for match in _PATTERN.finditer(output):
        busid, vendor_id, product_id, description = match.groups()
        # Strip trailing "(vid:pid)" that usbip appends to the description line
        desc = re.sub(r"\s+\(\w{4}:\w{4}\)\s*$", "", description.strip())
        vendor_name, _, product_name = desc.partition(" : ")
        devices.append(
            LocalDevice(
                busid=busid,
                busid_safe=busid.replace(".", "-"),
                vendor_id=vendor_id,
                product_id=product_id,
                vendor_name=vendor_name.strip() or "Unknown",
                product_name=product_name.strip() or "Unknown",
            )
        )
    return devices
