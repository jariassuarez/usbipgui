from pydantic import BaseModel


class LocalDevice(BaseModel):
    busid: str
    busid_safe: str      # busid with dots replaced by dashes (safe for HTML ids)
    vendor_id: str
    product_id: str
    vendor_name: str
    product_name: str
    is_exported: bool = False


class DaemonStatus(BaseModel):
    host_module_loaded: bool
    is_running: bool
    pid: int | None = None
