from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class SwProductRead(BaseModel):
    id: int
    asset_id: int
    collected_at: datetime
    name: Optional[str] = None
    version: Optional[str] = None
    vendor: Optional[str] = None
    install_date: Optional[date] = None
    raw_json: Optional[dict] = None
    model_config = {"from_attributes": True}


class SwHotfixRead(BaseModel):
    id: int
    asset_id: int
    collected_at: datetime
    hotfix_id: Optional[str] = None
    description: Optional[str] = None
    installed_on: Optional[date] = None
    installed_by: Optional[str] = None
    raw_json: Optional[dict] = None
    model_config = {"from_attributes": True}


class SwProcessRead(BaseModel):
    id: int
    asset_id: int
    collected_at: datetime
    process_name: Optional[str] = None
    pid: Optional[int] = None
    session_name: Optional[str] = None
    memory_kb: Optional[int] = None
    raw_json: Optional[dict] = None
    model_config = {"from_attributes": True}


class SwAccountRead(BaseModel):
    id: int
    asset_id: int
    collected_at: datetime
    account_name: Optional[str] = None
    enabled: Optional[bool] = None
    comment: Optional[str] = None
    raw_json: Optional[dict] = None
    model_config = {"from_attributes": True}


class SwConnectionRead(BaseModel):
    id: int
    asset_id: int
    collected_at: datetime
    protocol: Optional[str] = None
    local_address: Optional[str] = None
    remote_address: Optional[str] = None
    state: Optional[str] = None
    process_name: Optional[str] = None
    raw_json: Optional[dict] = None
    model_config = {"from_attributes": True}


class SwAllRead(BaseModel):
    products: list[SwProductRead] = []
    hotfixes: list[SwHotfixRead] = []
    processes: list[SwProcessRead] = []
    accounts: list[SwAccountRead] = []
    connections: list[SwConnectionRead] = []


class AccountStatusUpdate(BaseModel):
    disabled_account_ids: list[int] = []
