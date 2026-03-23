from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LayoutCreate(BaseModel):
    name: str
    page_key: str = "asset_list"
    columns_json: list[dict]
    is_default: bool = False


class LayoutUpdate(BaseModel):
    name: Optional[str] = None
    columns_json: Optional[list[dict]] = None
    is_default: Optional[bool] = None


class LayoutRead(BaseModel):
    id: int
    name: str
    page_key: str
    columns_json: list[dict]
    is_default: bool
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
