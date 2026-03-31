from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# --- Template ---

class FormTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str = "general"
    folder_id: Optional[int] = None


class FormTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    folder_id: Optional[int] = None
    is_active: Optional[bool] = None


class FormTemplateFolderCreate(BaseModel):
    name: str


class FormTemplateFolderUpdate(BaseModel):
    name: str


class FormTemplateFolderRead(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FormTemplateRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    file_name: str
    category: str
    folder_id: Optional[int] = None
    folder_name: Optional[str] = None
    folder_path: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    mapping_count: Optional[int] = 0

    model_config = {"from_attributes": True}


# --- Mapping ---

class FormMappingCreate(BaseModel):
    sheet_name: Optional[str] = None
    cell: str
    data_source: str
    field: str
    secondary_field: Optional[str] = None
    display_label: Optional[str] = None
    format: Optional[str] = None
    aggregate_mode: Optional[str] = None
    output_template: Optional[str] = None
    repeat_direction: Optional[str] = None
    repeat_max_rows: Optional[int] = None
    named_range_name: Optional[str] = None
    page_range_name: Optional[str] = None
    overflow_mode: Optional[str] = None
    block_start_row: Optional[int] = None
    block_end_row: Optional[int] = None
    block_start_col: Optional[str] = None
    block_end_col: Optional[str] = None
    page_subblock_count: Optional[int] = None
    page_subblock_width: Optional[int] = None
    sort_order: int = 0


class FormMappingUpdate(BaseModel):
    sheet_name: Optional[str] = None
    cell: Optional[str] = None
    data_source: Optional[str] = None
    field: Optional[str] = None
    secondary_field: Optional[str] = None
    display_label: Optional[str] = None
    format: Optional[str] = None
    aggregate_mode: Optional[str] = None
    output_template: Optional[str] = None
    repeat_direction: Optional[str] = None
    repeat_max_rows: Optional[int] = None
    named_range_name: Optional[str] = None
    page_range_name: Optional[str] = None
    overflow_mode: Optional[str] = None
    block_start_row: Optional[int] = None
    block_end_row: Optional[int] = None
    block_start_col: Optional[str] = None
    block_end_col: Optional[str] = None
    page_subblock_count: Optional[int] = None
    page_subblock_width: Optional[int] = None
    sort_order: Optional[int] = None


class FormMappingRead(BaseModel):
    id: int
    template_id: int
    sheet_name: Optional[str]
    cell: str
    data_source: str
    field: str
    secondary_field: Optional[str]
    display_label: Optional[str]
    format: Optional[str]
    aggregate_mode: Optional[str]
    output_template: Optional[str]
    repeat_direction: Optional[str]
    repeat_max_rows: Optional[int]
    named_range_name: Optional[str]
    page_range_name: Optional[str]
    overflow_mode: Optional[str]
    block_start_row: Optional[int]
    block_end_row: Optional[int]
    block_start_col: Optional[str]
    block_end_col: Optional[str]
    page_subblock_count: Optional[int]
    page_subblock_width: Optional[int]
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


class FormDataPreviewRow(BaseModel):
    row_index: int
    values: dict[str, str]


class FormDataPreviewResponse(BaseModel):
    asset_id: int
    data_source: str
    is_repeatable: bool = False
    total_rows: int = 0
    truncated: bool = False
    rows: list[FormDataPreviewRow]
