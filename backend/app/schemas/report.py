from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ColumnDef(BaseModel):
    header: str
    field: str
    width: int = 15


class ReportTemplateBase(BaseModel):
    name: str
    display_name: str
    data_source: str
    sheet_name: str
    columns: list[ColumnDef] = []
    header_color: str = "#1F4E79"
    is_active: bool = True


class ReportTemplateCreate(ReportTemplateBase):
    pass


class ReportTemplateUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    data_source: Optional[str] = None
    sheet_name: Optional[str] = None
    columns: Optional[list[ColumnDef]] = None
    header_color: Optional[str] = None
    is_active: Optional[bool] = None


class ReportTemplateRead(ReportTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
