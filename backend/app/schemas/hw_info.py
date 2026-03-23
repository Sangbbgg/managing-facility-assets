from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class HwSystemRead(BaseModel):
    id: int
    asset_id: int
    collected_at: datetime
    manufacturer: Optional[str] = None
    system_model: Optional[str] = None
    system_serial: Optional[str] = None
    system_uuid: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    os_build: Optional[str] = None
    os_arch: Optional[str] = None
    system_type: Optional[str] = None
    bios_version: Optional[str] = None
    total_memory_mb: Optional[int] = None
    hostname: Optional[str] = None
    domain: Optional[str] = None
    install_date: Optional[date] = None
    last_boot: Optional[datetime] = None
    raw_csproduct: Optional[dict] = None
    raw_os: Optional[dict] = None
    raw_systeminfo: Optional[dict] = None
    model_config = {"from_attributes": True}


class HwCpuRead(BaseModel):
    id: int
    asset_id: int
    collected_at: datetime
    name: Optional[str] = None
    manufacturer: Optional[str] = None
    cores: Optional[int] = None
    logical_cpus: Optional[int] = None
    max_clock_mhz: Optional[int] = None
    architecture: Optional[str] = None
    socket: Optional[str] = None
    raw_json: Optional[dict] = None
    model_config = {"from_attributes": True}


class HwMemoryRead(BaseModel):
    id: int
    asset_id: int
    collected_at: datetime
    locator: Optional[str] = None
    capacity_bytes: Optional[int] = None
    speed_mhz: Optional[int] = None
    manufacturer: Optional[str] = None
    serial_number: Optional[str] = None
    form_factor: Optional[str] = None
    raw_json: Optional[dict] = None
    model_config = {"from_attributes": True}


class HwDiskRead(BaseModel):
    id: int
    asset_id: int
    collected_at: datetime
    model: Optional[str] = None
    size_bytes: Optional[int] = None
    interface_type: Optional[str] = None
    serial_number: Optional[str] = None
    media_type: Optional[str] = None
    partitions: Optional[int] = None
    raw_json: Optional[dict] = None
    model_config = {"from_attributes": True}


class HwGpuRead(BaseModel):
    id: int
    asset_id: int
    collected_at: datetime
    name: Optional[str] = None
    driver_version: Optional[str] = None
    video_memory_mb: Optional[int] = None
    resolution: Optional[str] = None
    raw_json: Optional[dict] = None
    model_config = {"from_attributes": True}


class HwNicRead(BaseModel):
    id: int
    asset_id: int
    collected_at: datetime
    adapter_name: Optional[str] = None
    connection_name: Optional[str] = None
    mac_address: Optional[str] = None
    ipv4_address: Optional[str] = None
    subnet_mask: Optional[str] = None
    default_gateway: Optional[str] = None
    dhcp_enabled: Optional[bool] = None
    raw_json: Optional[dict] = None
    model_config = {"from_attributes": True}


class HwAllRead(BaseModel):
    systems: list[HwSystemRead] = []
    cpus: list[HwCpuRead] = []
    memories: list[HwMemoryRead] = []
    disks: list[HwDiskRead] = []
    gpus: list[HwGpuRead] = []
    nics: list[HwNicRead] = []
