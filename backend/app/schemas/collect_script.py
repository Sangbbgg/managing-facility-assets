from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CollectScriptUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    ps_command: Optional[str] = None
    is_active: Optional[bool] = None


class CollectScriptRead(BaseModel):
    id: int
    script_key: str
    display_name: str
    description: Optional[str] = None
    legacy_command: Optional[str] = None
    ps_filename: Optional[str] = None
    target_table: str
    output_format: str
    is_active: bool
    sort_order: int
    model_config = {"from_attributes": True}
