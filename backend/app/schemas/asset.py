from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class AssetCreate(BaseModel):
    asset_name: str
    group_id: int
    equipment_type_id: int
    purpose: Optional[str] = None
    importance: Optional[str] = None
    install_date: Optional[date] = None
    representative_nic_id: Optional[int] = None
    representative_account_id: Optional[int] = None
    location_id: Optional[int] = None
    manager_id: Optional[int] = None
    status: str = "OPERATING"


class AssetUpdate(BaseModel):
    asset_name: Optional[str] = None
    group_id: Optional[int] = None
    equipment_type_id: Optional[int] = None
    purpose: Optional[str] = None
    importance: Optional[str] = None
    install_date: Optional[date] = None
    representative_nic_id: Optional[int] = None
    representative_account_id: Optional[int] = None
    location_id: Optional[int] = None
    manager_id: Optional[int] = None
    status: Optional[str] = None


class AssetRead(BaseModel):
    id: int
    asset_code: str
    asset_name: str
    purpose: Optional[str] = None
    importance: Optional[str] = None
    install_date: Optional[date] = None
    ip_address: Optional[str] = None
    representative_nic_id: Optional[int] = None
    representative_account_id: Optional[int] = None
    representative_account_name: Optional[str] = None
    status: str
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    group_id: Optional[int] = None
    location_id: Optional[int] = None
    equipment_type_id: Optional[int] = None
    manager_id: Optional[int] = None
    last_collected_at: Optional[datetime] = None
    custom_fields_json: Optional[dict] = None

    model_config = {"from_attributes": True}


class AssetDetailListItem(BaseModel):
    id: int
    asset_code: str
    asset_name: str
    purpose: Optional[str] = None
    importance: Optional[str] = None
    install_date: Optional[date] = None
    status: Optional[str] = None
    ip_address: Optional[str] = None
    representative_nic_id: Optional[int] = None
    representative_account_id: Optional[int] = None
    representative_account_name: Optional[str] = None
    last_collected_at: Optional[datetime] = None
    group_id: Optional[int] = None
    group_name: Optional[str] = None
    group_full_path: Optional[str] = None
    group_code: Optional[str] = None
    group_display_code: Optional[str] = None
    location_id: Optional[int] = None
    location_name: Optional[str] = None
    location_full_path: Optional[str] = None
    equipment_type_id: Optional[int] = None
    equipment_type_name: Optional[str] = None
    equipment_type_code: Optional[str] = None
    manager_id: Optional[int] = None
    manager_name: Optional[str] = None
    resolved_manager_id: Optional[int] = None
    resolved_manager_name: Optional[str] = None
    custom_fields_json: Optional[dict] = None
