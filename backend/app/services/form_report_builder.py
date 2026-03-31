import re
import tempfile
from copy import copy
from datetime import date, datetime
from typing import Any
import json

from openpyxl import load_workbook
from openpyxl.utils import column_index_from_string
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset
from app.models.collection import AssetCollectRun, AssetNetworkConnection
from app.models.form_template import ReportFormMapping, ReportFormTemplate
from app.models.hw_info import AssetHwCpu, AssetHwDisk, AssetHwGpu, AssetHwMemory, AssetHwNic, AssetHwOptical, AssetHwSystem
from app.models.record import ConsoleAccessRecord, EventLogRecord, InspectionRecord, PasswordRecord, SealRecord
from app.models.sw_info import AssetSwAccount, AssetSwHotfix, AssetSwProcess, AssetSwProduct
from app.schemas.form_template import FormFieldInfo


_EXCLUDED_FIELDS = {
    "id",
    "asset_id",
    "parent_id",
    "group_id",
    "location_id",
    "equipment_type_id",
    "manager_id",
    "dept_id",
    "representative_nic_id",
    "representative_account_id",
    "is_deleted",
    "depth",
    "code",
    "key",
    "raw_json",
    "raw_payload",
    "raw_csproduct",
    "raw_os",
    "raw_systeminfo",
}

_ASSET_DERIVED_FIELDS = [
    ("group_name", "Group Name"),
    ("group_full_path", "Group Full Path"),
    ("location_name", "Location Name"),
    ("location_full_path", "Location Full Path"),
    ("equipment_type_name", "Equipment Type Name"),
    ("manager_name", "Manager Name"),
    ("manager_title", "Manager Title"),
    ("manager_contact", "Manager Contact"),
    ("ip_address", "Representative IP"),
]

_DATA_SOURCE_MODELS: dict[str, tuple[Any, bool, Any | None]] = {
    "hw_system": (AssetHwSystem, False, None),
    "hw_cpu": (AssetHwCpu, True, AssetHwCpu.collected_at.desc()),
    "hw_memory": (AssetHwMemory, True, AssetHwMemory.collected_at.desc()),
    "hw_disk": (AssetHwDisk, True, AssetHwDisk.collected_at.desc()),
    "hw_optical": (AssetHwOptical, True, AssetHwOptical.collected_at.desc()),
    "hw_gpu": (AssetHwGpu, True, AssetHwGpu.collected_at.desc()),
    "hw_nic": (AssetHwNic, True, AssetHwNic.collected_at.desc()),
    "sw_product": (AssetSwProduct, True, AssetSwProduct.collected_at.desc()),
    "sw_hotfix": (AssetSwHotfix, True, AssetSwHotfix.installed_on.desc()),
    "sw_process": (AssetSwProcess, True, AssetSwProcess.collected_at.desc()),
    "sw_account": (AssetSwAccount, True, AssetSwAccount.collected_at.desc()),
    "network_connection": (AssetNetworkConnection, True, AssetNetworkConnection.collected_at.desc()),
    "collect_run": (AssetCollectRun, True, AssetCollectRun.collected_at.desc()),
    "inspection": (InspectionRecord, True, InspectionRecord.record_date.desc()),
    "event_log": (EventLogRecord, True, EventLogRecord.record_date.desc()),
    "console_access": (ConsoleAccessRecord, True, ConsoleAccessRecord.access_date.desc()),
    "seal": (SealRecord, True, SealRecord.record_date.desc()),
    "password": (PasswordRecord, True, PasswordRecord.changed_date.desc()),
}


def _humanize_label(field: str) -> str:
    return field.replace("_", " ").title()


def _build_field_catalog() -> list[FormFieldInfo]:
    catalog: list[FormFieldInfo] = []

    for column in Asset.__table__.columns:
        if column.name in _EXCLUDED_FIELDS:
            continue
        catalog.append(
            FormFieldInfo(
                data_source="asset",
                field=column.name,
                label=_humanize_label(column.name),
            )
        )

    for field_name, label in _ASSET_DERIVED_FIELDS:
        catalog.append(
            FormFieldInfo(
                data_source="asset",
                field=field_name,
                label=label,
            )
        )

    for data_source, (model, is_repeatable, _order_by) in _DATA_SOURCE_MODELS.items():
        for column in model.__table__.columns:
            if column.name in _EXCLUDED_FIELDS:
                continue
            catalog.append(
                FormFieldInfo(
                    data_source=data_source,
                    field=column.name,
                    label=_humanize_label(column.name),
                    is_repeatable=is_repeatable,
                )
            )

    catalog.extend([
        FormFieldInfo(data_source="static", field="(direct-input)", label="Static Text", example="No issue found"),
        FormFieldInfo(data_source="today", field="date", label="Today Date", example="2026-03-30"),
        FormFieldInfo(data_source="today", field="year", label="Year", example="2026"),
        FormFieldInfo(data_source="today", field="month", label="Month", example="03"),
        FormFieldInfo(data_source="today", field="day", label="Day", example="30"),
        FormFieldInfo(data_source="today", field="weekday", label="Weekday", example="Monday"),
    ])

    return catalog


FIELD_CATALOG: list[FormFieldInfo] = _build_field_catalog()


def _stringify_preview_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (date, datetime)):
        return str(value)
    if isinstance(value, (list, dict)):
        try:
            return json.dumps(value, ensure_ascii=False)
        except TypeError:
            return str(value)
    return str(value)


def parse_cell(cell_str: str) -> tuple[int, int]:
    matched = re.match(r"([A-Z]+)(\d+)", cell_str.upper())
    if not matched:
        raise ValueError(f"invalid cell address: {cell_str}")
    col = column_index_from_string(matched.group(1))
    row = int(matched.group(2))
    return row, col


def _is_merged_child(ws, row: int, col: int) -> bool:
    for mr in ws.merged_cells.ranges:
        if mr.min_row <= row <= mr.max_row and mr.min_col <= col <= mr.max_col:
            return not (mr.min_row == row and mr.min_col == col)
    return False


def _resolve_repeat_target(ws, base_row: int, base_col: int, direction: str, index: int) -> tuple[int, int]:
    if direction == "down":
        target_row = base_row + index
        while _is_merged_child(ws, target_row, base_col):
            target_row += 1
        return target_row, base_col

    target_col = base_col
    steps = index
    while steps > 0:
        target_col += 1
        while _is_merged_child(ws, base_row, target_col):
            target_col += 1
        steps -= 1
    return base_row, target_col


async def fetch_asset_data(asset_id: int, db: AsyncSession) -> dict:
    from app.models.master import EquipmentType, GroupNode, LocationNode, Person
    from sqlalchemy.orm import aliased

    Manager = aliased(Person)
    RepresentativeNic = aliased(AssetHwNic)

    stmt = (
        select(Asset, GroupNode, LocationNode, EquipmentType, Manager, RepresentativeNic)
        .outerjoin(GroupNode, Asset.group_id == GroupNode.id)
        .outerjoin(LocationNode, Asset.location_id == LocationNode.id)
        .outerjoin(EquipmentType, Asset.equipment_type_id == EquipmentType.id)
        .outerjoin(Manager, Asset.manager_id == Manager.id)
        .outerjoin(RepresentativeNic, Asset.representative_nic_id == RepresentativeNic.id)
        .where(Asset.id == asset_id)
    )
    row = (await db.execute(stmt)).first()
    if not row:
        return {}

    asset, group, location, equipment_type, manager, representative_nic = row
    data = {
        column.name: getattr(asset, column.name)
        for column in Asset.__table__.columns
        if column.name not in _EXCLUDED_FIELDS
    }
    data.update({
        "ip_address": representative_nic.ipv4_address if representative_nic else "",
        "group_name": group.name if group else "",
        "group_full_path": group.full_path if group else "",
        "location_name": location.name if location else "",
        "location_full_path": location.full_path if location else "",
        "equipment_type_name": equipment_type.name if equipment_type else "",
        "manager_name": manager.name if manager else "",
        "manager_title": manager.title if manager else "",
        "manager_contact": manager.contact if manager else "",
    })
    return data


def _serialize_model_row(row: Any) -> dict:
    return {
        column.name: getattr(row, column.name)
        for column in row.__table__.columns
        if column.name not in _EXCLUDED_FIELDS
    }


async def _fetch_single_row(model: Any, asset_id: int, db: AsyncSession) -> dict:
    stmt = select(model).where(model.asset_id == asset_id).limit(1)
    row = (await db.execute(stmt)).scalar_one_or_none()
    if not row:
        return {}
    return _serialize_model_row(row)


async def _fetch_multi_rows(model: Any, asset_id: int, db: AsyncSession, order_by: Any | None = None) -> list[dict]:
    stmt = select(model).where(model.asset_id == asset_id)
    if order_by is not None:
        stmt = stmt.order_by(order_by)
    rows = (await db.execute(stmt)).scalars().all()
    return [_serialize_model_row(row) for row in rows]


async def fetch_data_source(data_source: str, asset_id: int, db: AsyncSession):
    if data_source == "asset":
        return await fetch_asset_data(asset_id, db)

    if data_source == "hw_system":
        return await _fetch_single_row(AssetHwSystem, asset_id, db)

    if data_source in _DATA_SOURCE_MODELS:
        model, is_repeatable, order_by = _DATA_SOURCE_MODELS[data_source]
        if is_repeatable:
            rows = await _fetch_multi_rows(model, asset_id, db, order_by)
            if data_source == "inspection":
                for row in rows:
                    if row.get("check_items") is not None:
                        row["check_items"] = str(row["check_items"])
            return rows
        return await _fetch_single_row(model, asset_id, db)

    if data_source == "today":
        now = datetime.now()
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return {
            "date": now.strftime("%Y-%m-%d"),
            "year": str(now.year),
            "month": f"{now.month:02d}",
            "day": f"{now.day:02d}",
            "weekday": weekdays[now.weekday()],
        }

    if data_source == "static":
        return {}

    return {}


async def build_data_source_preview(
    data_source: str,
    asset_id: int,
    db: AsyncSession,
    max_rows: int = 5,
) -> dict[str, Any]:
    data = await fetch_data_source(data_source, asset_id, db)
    catalog_items = [item for item in FIELD_CATALOG if item.data_source == data_source]
    field_names = [item.field for item in catalog_items]

    if isinstance(data, list):
        rows = []
        for index, item in enumerate(data[:max_rows], start=1):
            rows.append({
                "row_index": index,
                "values": {
                    field: _stringify_preview_value(item.get(field))
                    for field in field_names
                },
            })
        return {
            "asset_id": asset_id,
            "data_source": data_source,
            "is_repeatable": True,
            "total_rows": len(data),
            "truncated": len(data) > max_rows,
            "rows": rows,
        }

    row_values = {
        field: _stringify_preview_value(data.get(field) if isinstance(data, dict) else None)
        for field in field_names
    }
    return {
        "asset_id": asset_id,
        "data_source": data_source,
        "is_repeatable": False,
        "total_rows": 1 if any(value != "" for value in row_values.values()) else 0,
        "truncated": False,
        "rows": [{
            "row_index": 1,
            "values": row_values,
        }],
    }


def format_value(value, fmt) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        return str(value)
    if fmt is None:
        return str(value)
    if "YYYY" in fmt and isinstance(value, (date, datetime)):
        return (
            fmt.replace("YYYY", str(value.year))
            .replace("MM", f"{value.month:02d}")
            .replace("DD", f"{value.day:02d}")
        )
    if "#" in fmt:
        try:
            return f"{float(value):,.0f}"
        except (ValueError, TypeError):
            return str(value)
    return str(value)


def extract_mapped_value(data: Any, field: str):
    if not field:
        return ""
    if isinstance(data, dict):
        return data.get(field, "")
    if isinstance(data, list):
        if not data:
            return ""
        first_row = data[0]
        if isinstance(first_row, dict):
            return first_row.get(field, "")
    return ""


def _extract_list_field_values(data: Any, field: str) -> list[Any]:
    if not isinstance(data, list):
        return []
    values = []
    for item in data:
        if isinstance(item, dict):
            value = item.get(field, "")
            if value not in (None, ""):
                values.append(value)
    return values


def resolve_mapping_value(data: Any, mapping, count_value: int | None = None) -> str:
    aggregate_mode = getattr(mapping, "aggregate_mode", None) or "value"
    raw_value = extract_mapped_value(data, mapping.field)
    secondary_raw_value = extract_mapped_value(data, getattr(mapping, "secondary_field", None))
    formatted_value = format_value(raw_value, mapping.format)
    secondary_formatted_value = format_value(secondary_raw_value, mapping.format)

    if isinstance(data, list):
        values = _extract_list_field_values(data, mapping.field)
        if aggregate_mode in {"value", "first"}:
            formatted_value = format_value(values[0] if values else "", mapping.format)
        elif aggregate_mode == "count":
            formatted_value = str(len(data))
        elif aggregate_mode == "join":
            formatted_value = ", ".join(format_value(value, mapping.format) for value in values)
        elif aggregate_mode == "join_unique":
            unique_values = list(dict.fromkeys(values))
            formatted_value = ", ".join(format_value(value, mapping.format) for value in unique_values)

    derived_count_value = 0
    if isinstance(data, list):
        derived_count_value = len(data)
    elif isinstance(data, dict):
        derived_count_value = 1 if raw_value not in (None, "") else 0
    if count_value is None:
        count_value = derived_count_value

    output_template = getattr(mapping, "output_template", None)
    if output_template:
        return (
            output_template
            .replace("{value}", formatted_value)
            .replace("{secondary}", secondary_formatted_value)
            .replace("{count}", str(count_value))
        )
    return formatted_value


async def generate_form_report(template_id: int, asset_id: int, db: AsyncSession) -> tuple[str, str]:
    template = await db.get(ReportFormTemplate, template_id)
    if not template:
        raise ValueError("form template not found")

    stmt = (
        select(ReportFormMapping)
        .where(ReportFormMapping.template_id == template_id)
        .order_by(ReportFormMapping.sort_order)
    )
    mappings = (await db.execute(stmt)).scalars().all()

    data_cache: dict[str, Any] = {}

    async def get_data(source: str):
        if source not in data_cache:
            data_cache[source] = await fetch_data_source(source, asset_id, db)
        return data_cache[source]

    wb = load_workbook(template.file_path)

    for mapping in mappings:
        if mapping.repeat_direction:
            continue
        ws = wb[mapping.sheet_name] if mapping.sheet_name and mapping.sheet_name in wb.sheetnames else wb.active
        row, col = parse_cell(mapping.cell)
        if mapping.data_source == "static":
            ws.cell(row, col).value = mapping.field
            continue
        data = await get_data(mapping.data_source)
        ws.cell(row, col).value = resolve_mapping_value(data, mapping)

    repeat_groups: dict[tuple[str, str, str, int], list[tuple[ReportFormMapping, int, int]]] = {}
    for mapping in mappings:
        if not mapping.repeat_direction:
            continue
        row, col = parse_cell(mapping.cell)
        direction = mapping.repeat_direction or "down"
        anchor = row if direction == "down" else col
        key = (mapping.sheet_name or "", mapping.data_source, direction, anchor)
        repeat_groups.setdefault(key, []).append((mapping, row, col))

    for (_sheet_name, data_source, direction, _anchor), group in repeat_groups.items():
        data = await get_data(data_source)
        if not isinstance(data, list):
            continue
        max_rows = group[0][0].repeat_max_rows or 50
        for index, item in enumerate(data[:max_rows]):
            for mapping, base_row, base_col in group:
                ws = wb[mapping.sheet_name] if mapping.sheet_name and mapping.sheet_name in wb.sheetnames else wb.active
                target_row, target_col = _resolve_repeat_target(ws, base_row, base_col, direction, index)
                ws.cell(target_row, target_col).value = resolve_mapping_value(
                    item,
                    mapping,
                    count_value=len(data),
                )
                if index > 0:
                    src_cell = ws.cell(base_row, base_col)
                    tgt_cell = ws.cell(target_row, target_col)
                    if src_cell.has_style:
                        tgt_cell.font = copy(src_cell.font)
                        tgt_cell.fill = copy(src_cell.fill)
                        tgt_cell.border = copy(src_cell.border)
                        tgt_cell.alignment = copy(src_cell.alignment)
                        tgt_cell.number_format = src_cell.number_format

    asset_data = await get_data("asset")
    asset_code = asset_data.get("asset_code", "unknown") if isinstance(asset_data, dict) else "unknown"
    file_name = f"{template.name}_{asset_code}_{date.today()}.xlsx"

    tmp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
    wb.save(tmp.name)
    return tmp.name, file_name
