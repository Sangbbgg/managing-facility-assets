from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class AssetCreate(BaseModel):
    asset_name: str
    group_id: int
    equipment_type_id: int
    purpose: Optional[str] = None
    model_name: Optional[str] = None
    serial_number: Optional[str] = None
    importance: Optional[str] = None
    install_date: Optional[date] = None
    ip_address: Optional[str] = None
    location_id: Optional[int] = None
    os_id: Optional[int] = None
    av_id: Optional[int] = None
    manager_id: Optional[int] = None
    supervisor_id: Optional[int] = None
    status: str = "OPERATING"


class AssetUpdate(BaseModel):
    asset_name: Optional[str] = None
    group_id: Optional[int] = None
    equipment_type_id: Optional[int] = None
    purpose: Optional[str] = None
    model_name: Optional[str] = None
    serial_number: Optional[str] = None
    importance: Optional[str] = None
    install_date: Optional[date] = None
    ip_address: Optional[str] = None
    location_id: Optional[int] = None
    os_id: Optional[int] = None
    av_id: Optional[int] = None
    manager_id: Optional[int] = None
    supervisor_id: Optional[int] = None
    status: Optional[str] = None


class AssetRead(BaseModel):
    id: int
    asset_code: str
    asset_name: str
    purpose: Optional[str] = None
    model_name: Optional[str] = None
    serial_number: Optional[str] = None
    importance: Optional[str] = None
    install_date: Optional[date] = None
    ip_address: Optional[str] = None
    status: str
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    group_id: Optional[int] = None
    location_id: Optional[int] = None
    equipment_type_id: Optional[int] = None
    os_id: Optional[int] = None
    av_id: Optional[int] = None
    manager_id: Optional[int] = None
    supervisor_id: Optional[int] = None
    model_config = {"from_attributes": True}
