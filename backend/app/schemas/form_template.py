from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# --- Template ---

class FormTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str = "general"


class FormTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class FormTemplateRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    file_name: str
    category: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    mapping_count: Optional[int] = 0

    model_config = {"from_attributes": True}


# --- Mapping ---

class FormMappingCreate(BaseModel):
    cell: str
    data_source: str
    field: str
    display_label: Optional[str] = None
    format: Optional[str] = None
    repeat_direction: Optional[str] = None
    repeat_max_rows: Optional[int] = None
    sort_order: int = 0


class FormMappingUpdate(BaseModel):
    cell: Optional[str] = None
    data_source: Optional[str] = None
    field: Optional[str] = None
    display_label: Optional[str] = None
    format: Optional[str] = None
    repeat_direction: Optional[str] = None
    repeat_max_rows: Optional[int] = None
    sort_order: Optional[int] = None


class FormMappingRead(BaseModel):
    id: int
    template_id: int
    cell: str
    data_source: str
    field: str
    display_label: Optional[str]
    format: Optional[str]
    repeat_direction: Optional[str]
    repeat_max_rows: Optional[int]
    sort_order: int

    model_config = {"from_attributes": True}


# --- Bulk Mapping ---

class FormMappingBulkSave(BaseModel):
    mappings: list[FormMappingCreate]


# --- 보고서 생성 요청 ---

class FormReportRequest(BaseModel):
    template_id: int
    asset_id: int


# --- 미리보기용 필드 카탈로그 ---

class FormFieldInfo(BaseModel):
    data_source: str
    field: str
    label: str
    example: Optional[str] = None
    is_repeatable: bool = False
