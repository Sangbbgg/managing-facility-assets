import re
import tempfile
from copy import copy
from datetime import date, datetime

from openpyxl import load_workbook
from openpyxl.utils import column_index_from_string
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.form_template import ReportFormMapping, ReportFormTemplate
from app.schemas.form_template import FormFieldInfo


FIELD_CATALOG: list[FormFieldInfo] = [
    FormFieldInfo(data_source="asset", field="asset_code", label="자산코드", example="IC-GT1-SER-0001"),
    FormFieldInfo(data_source="asset", field="asset_name", label="자산명", example="메인DB서버"),
    FormFieldInfo(data_source="asset", field="ip_address", label="IP주소", example="10.10.1.10"),
    FormFieldInfo(data_source="asset", field="purpose", label="용도"),
    FormFieldInfo(data_source="asset", field="importance", label="중요도", example="상"),
    FormFieldInfo(data_source="asset", field="status", label="상태", example="OPERATING"),
    FormFieldInfo(data_source="asset", field="install_date", label="설치일자"),
    FormFieldInfo(data_source="asset", field="group_name", label="운영그룹명"),
    FormFieldInfo(data_source="asset", field="group_full_path", label="운영그룹 경로"),
    FormFieldInfo(data_source="asset", field="location_name", label="설치장소명"),
    FormFieldInfo(data_source="asset", field="location_full_path", label="설치장소 경로"),
    FormFieldInfo(data_source="asset", field="equipment_type_name", label="장비종류"),
    FormFieldInfo(data_source="asset", field="manager_name", label="담당자명"),
    FormFieldInfo(data_source="asset", field="manager_title", label="담당자직급"),
    FormFieldInfo(data_source="asset", field="manager_contact", label="담당자연락처"),
    FormFieldInfo(data_source="hw_system", field="manufacturer", label="HW 제조사"),
    FormFieldInfo(data_source="hw_system", field="system_model", label="HW 모델"),
    FormFieldInfo(data_source="hw_system", field="system_serial", label="HW 시리얼"),
    FormFieldInfo(data_source="hw_system", field="os_name", label="HW OS명"),
    FormFieldInfo(data_source="hw_system", field="bios_version", label="BIOS 버전"),
    FormFieldInfo(data_source="hw_cpu", field="name", label="CPU명", is_repeatable=True),
    FormFieldInfo(data_source="hw_cpu", field="cores", label="CPU 코어수", is_repeatable=True),
    FormFieldInfo(data_source="hw_cpu", field="max_clock_mhz", label="CPU 클럭(MHz)", is_repeatable=True),
    FormFieldInfo(data_source="hw_memory", field="locator", label="메모리 슬롯", is_repeatable=True),
    FormFieldInfo(data_source="hw_memory", field="capacity_bytes", label="메모리 용량(Byte)", is_repeatable=True),
    FormFieldInfo(data_source="hw_memory", field="speed_mhz", label="메모리 속도(MHz)", is_repeatable=True),
    FormFieldInfo(data_source="hw_disk", field="model", label="디스크 모델", is_repeatable=True),
    FormFieldInfo(data_source="hw_disk", field="size_bytes", label="디스크 용량(Byte)", is_repeatable=True),
    FormFieldInfo(data_source="hw_disk", field="interface_type", label="디스크 인터페이스", is_repeatable=True),
    FormFieldInfo(data_source="hw_nic", field="adapter_name", label="NIC명", is_repeatable=True),
    FormFieldInfo(data_source="hw_nic", field="mac_address", label="MAC주소", is_repeatable=True),
    FormFieldInfo(data_source="hw_nic", field="ipv4_address", label="NIC IP", is_repeatable=True),
    FormFieldInfo(data_source="inspection", field="record_date", label="점검일자", is_repeatable=True),
    FormFieldInfo(data_source="inspection", field="check_items", label="점검항목", is_repeatable=True),
    FormFieldInfo(data_source="inspection", field="result", label="점검결과", is_repeatable=True),
    FormFieldInfo(data_source="inspection", field="special_notes", label="특이사항", is_repeatable=True),
    FormFieldInfo(data_source="inspection", field="inspector", label="점검자", is_repeatable=True),
    FormFieldInfo(data_source="static", field="(직접입력)", label="고정 텍스트", example="신인천빛드림본부"),
    FormFieldInfo(data_source="today", field="date", label="오늘 날짜", example="2026년 03월 24일"),
    FormFieldInfo(data_source="today", field="year", label="올해 연도", example="2026"),
    FormFieldInfo(data_source="today", field="month", label="이번 달", example="03"),
    FormFieldInfo(data_source="today", field="day", label="오늘 일", example="24"),
    FormFieldInfo(data_source="today", field="weekday", label="오늘 요일", example="화요일"),
]


def parse_cell(cell_str: str) -> tuple[int, int]:
    matched = re.match(r"([A-Z]+)(\d+)", cell_str.upper())
    if not matched:
        raise ValueError(f"잘못된 셀 주소: {cell_str}")
    col = column_index_from_string(matched.group(1))
    row = int(matched.group(2))
    return row, col


async def fetch_asset_data(asset_id: int, db: AsyncSession) -> dict:
    from app.models.asset import Asset
    from app.models.hw_info import AssetHwNic
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
    return {
        "asset_code": asset.asset_code,
        "asset_name": asset.asset_name,
        "ip_address": representative_nic.ipv4_address if representative_nic else "",
        "purpose": asset.purpose,
        "importance": asset.importance,
        "status": asset.status,
        "install_date": str(asset.install_date) if asset.install_date else "",
        "group_name": group.name if group else "",
        "group_full_path": group.full_path if group else "",
        "location_name": location.name if location else "",
        "location_full_path": location.full_path if location else "",
        "equipment_type_name": equipment_type.name if equipment_type else "",
        "manager_name": manager.name if manager else "",
        "manager_title": manager.title if manager else "",
        "manager_contact": manager.contact if manager else "",
    }


async def fetch_data_source(data_source: str, asset_id: int, db: AsyncSession):
    if data_source == "asset":
        return await fetch_asset_data(asset_id, db)

    if data_source == "hw_system":
        from app.models.hw_info import AssetHwSystem

        stmt = select(AssetHwSystem).where(AssetHwSystem.asset_id == asset_id).limit(1)
        row = (await db.execute(stmt)).scalar_one_or_none()
        if not row:
            return {}
        return {c.name: getattr(row, c.name) for c in AssetHwSystem.__table__.columns if c.name not in ("id", "asset_id")}

    if data_source.startswith("hw_"):
        model_map = {
            "hw_cpu": "AssetHwCpu",
            "hw_memory": "AssetHwMemory",
            "hw_disk": "AssetHwDisk",
            "hw_gpu": "AssetHwGpu",
            "hw_nic": "AssetHwNic",
        }
        import app.models.hw_info as hw_mod

        model = getattr(hw_mod, model_map[data_source])
        stmt = select(model).where(model.asset_id == asset_id)
        rows = (await db.execute(stmt)).scalars().all()
        return [
            {c.name: getattr(r, c.name) for c in model.__table__.columns if c.name not in ("id", "asset_id")}
            for r in rows
        ]

    if data_source == "inspection":
        from app.models.record import InspectionRecord

        stmt = (
            select(InspectionRecord)
            .where(InspectionRecord.asset_id == asset_id)
            .order_by(InspectionRecord.record_date.desc())
            .limit(20)
        )
        rows = (await db.execute(stmt)).scalars().all()
        return [
            {
                "record_date": str(r.record_date),
                "inspection_type": r.inspection_type,
                "check_items": str(r.check_items) if r.check_items else "",
                "result": r.result or "",
                "special_notes": r.special_notes or "",
                "inspector": r.inspector or "",
            }
            for r in rows
        ]

    if data_source == "today":
        now = datetime.now()
        weekdays = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
        return {
            "date": now.strftime("%Y년 %m월 %d일"),
            "year": str(now.year),
            "month": f"{now.month:02d}",
            "day": f"{now.day:02d}",
            "weekday": weekdays[now.weekday()],
        }

    if data_source == "static":
        return {}

    return {}


def format_value(value, fmt) -> str:
    if value is None:
        return ""
    if fmt is None:
        return str(value)
    if "YYYY" in fmt and isinstance(value, (date, datetime)):
        return fmt.replace("YYYY", str(value.year)).replace("MM", f"{value.month:02d}").replace("DD", f"{value.day:02d}")
    if "#" in fmt:
        try:
            return f"{float(value):,.0f}"
        except (ValueError, TypeError):
            return str(value)
    return str(value)


async def generate_form_report(template_id: int, asset_id: int, db: AsyncSession) -> tuple[str, str]:
    template = await db.get(ReportFormTemplate, template_id)
    if not template:
        raise ValueError("서식을 찾을 수 없습니다")

    stmt = select(ReportFormMapping).where(ReportFormMapping.template_id == template_id).order_by(ReportFormMapping.sort_order)
    mappings = (await db.execute(stmt)).scalars().all()

    data_cache: dict = {}

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
        if isinstance(data, dict):
            ws.cell(row, col).value = format_value(data.get(mapping.field, ""), mapping.format)

    repeat_groups: dict = {}
    for mapping in mappings:
        if not mapping.repeat_direction:
            continue
        row, col = parse_cell(mapping.cell)
        key = (mapping.sheet_name or "", mapping.data_source, row)
        repeat_groups.setdefault(key, []).append((mapping, row, col))

    for (_sheet_name, data_source, _start_row), group in repeat_groups.items():
        data = await get_data(data_source)
        if not isinstance(data, list):
            continue
        max_rows = group[0][0].repeat_max_rows or 50
        for index, item in enumerate(data[:max_rows]):
            for mapping, base_row, base_col in group:
                ws = wb[mapping.sheet_name] if mapping.sheet_name and mapping.sheet_name in wb.sheetnames else wb.active
                target_row = base_row + index
                value = item.get(mapping.field, "")
                ws.cell(target_row, base_col).value = format_value(value, mapping.format)
                if index > 0:
                    src_cell = ws.cell(base_row, base_col)
                    tgt_cell = ws.cell(target_row, base_col)
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
