from pydantic import BaseModel


class RemoteDevice(BaseModel):
    busid: str
    busid_safe: str      # busid with dots replaced by dashes (safe for HTML ids)
    vendor_id: str
    product_id: str
    vendor_name: str
    product_name: str


class AttachedPort(BaseModel):
    port: int
    speed: str
    vendor_id: str
    product_id: str
    remote_host: str
    remote_busid: str
