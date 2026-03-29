from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CustomFieldCreate(BaseModel):
    field_key: str
    field_value: str
    sort_order: int = 0


class CustomFieldUpdate(BaseModel):
    field_key: Optional[str] = None
    field_value: Optional[str] = None
    sort_order: Optional[int] = None


class CustomFieldRead(BaseModel):
    id: int
    asset_id: int
    field_key: str
    field_value: str
    sort_order: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class CustomFieldKeyCreate(BaseModel):
    field_key: str


class CustomFieldValueUpsert(BaseModel):
    field_value: str = ""
