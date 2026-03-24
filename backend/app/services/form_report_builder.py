import tempfile
import re
from datetime import date, datetime
from pathlib import Path
from copy import copy
from openpyxl import load_workbook
from openpyxl.utils import column_index_from_string
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.form_template import ReportFormTemplate, ReportFormMapping
from app.schemas.form_template import FormFieldInfo


# ─── 필드 카탈로그 ───

FIELD_CATALOG: list[FormFieldInfo] = [
    # asset (단건)
    FormFieldInfo(data_source="asset", field="asset_code", label="자산코드", example="IC-GT1-SER-0001"),
    FormFieldInfo(data_source="asset", field="asset_name", label="자산명", example="메인DB서버"),
    FormFieldInfo(data_source="asset", field="model_name", label="모델명", example="PowerEdge R750"),
    FormFieldInfo(data_source="asset", field="serial_number", label="시리얼넘버"),
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
    FormFieldInfo(data_source="asset", field="os_name", label="OS명"),
    FormFieldInfo(data_source="asset", field="os_version", label="OS버전"),
    FormFieldInfo(data_source="asset", field="av_name", label="백신명"),
    FormFieldInfo(data_source="asset", field="av_version", label="백신버전"),
    FormFieldInfo(data_source="asset", field="manager_name", label="담당자명"),
    FormFieldInfo(data_source="asset", field="manager_dept", label="담당자 부서"),
    FormFieldInfo(data_source="asset", field="manager_title", label="담당자 직급"),
    FormFieldInfo(data_source="asset", field="manager_contact", label="담당자 연락처"),
    FormFieldInfo(data_source="asset", field="supervisor_name", label="관리책임자명"),
    FormFieldInfo(data_source="asset", field="supervisor_dept", label="관리책임자 부서"),
    FormFieldInfo(data_source="asset", field="supervisor_title", label="관리책임자 직급"),
    # hw_system (단건)
    FormFieldInfo(data_source="hw_system", field="manufacturer", label="HW 제조사"),
    FormFieldInfo(data_source="hw_system", field="model", label="HW 모델"),
    FormFieldInfo(data_source="hw_system", field="serial_number", label="HW 시리얼"),
    FormFieldInfo(data_source="hw_system", field="os_name", label="HW OS명"),
    FormFieldInfo(data_source="hw_system", field="bios_version", label="BIOS 버전"),
    # hw_cpu (다건)
    FormFieldInfo(data_source="hw_cpu", field="name", label="CPU명", is_repeatable=True),
    FormFieldInfo(data_source="hw_cpu", field="cores", label="CPU 코어수", is_repeatable=True),
    FormFieldInfo(data_source="hw_cpu", field="clock_mhz", label="CPU 클럭(MHz)", is_repeatable=True),
    # hw_memory (다건)
    FormFieldInfo(data_source="hw_memory", field="slot", label="메모리 슬롯", is_repeatable=True),
    FormFieldInfo(data_source="hw_memory", field="capacity_gb", label="메모리 용량(GB)", is_repeatable=True),
    FormFieldInfo(data_source="hw_memory", field="speed_mhz", label="메모리 속도(MHz)", is_repeatable=True),
    # hw_disk (다건)
    FormFieldInfo(data_source="hw_disk", field="model", label="디스크 모델", is_repeatable=True),
    FormFieldInfo(data_source="hw_disk", field="capacity_gb", label="디스크 용량(GB)", is_repeatable=True),
    FormFieldInfo(data_source="hw_disk", field="interface_type", label="디스크 인터페이스", is_repeatable=True),
    # hw_nic (다건)
    FormFieldInfo(data_source="hw_nic", field="name", label="NIC명", is_repeatable=True),
    FormFieldInfo(data_source="hw_nic", field="mac_address", label="MAC주소", is_repeatable=True),
    FormFieldInfo(data_source="hw_nic", field="ip_address", label="NIC IP", is_repeatable=True),
    # inspection (다건)
    FormFieldInfo(data_source="inspection", field="record_date", label="점검일자", is_repeatable=True),
    FormFieldInfo(data_source="inspection", field="check_items", label="점검항목", is_repeatable=True),
    FormFieldInfo(data_source="inspection", field="result", label="점검결과", is_repeatable=True),
    FormFieldInfo(data_source="inspection", field="special_notes", label="특이사항", is_repeatable=True),
    FormFieldInfo(data_source="inspection", field="inspector", label="점검자", is_repeatable=True),
    # static / today
    FormFieldInfo(data_source="static", field="(직접입력)", label="고정 텍스트", example="신인천빛드림본부"),
    FormFieldInfo(data_source="today", field="date", label="오늘 날짜", example="2026년 03월 24일"),
    FormFieldInfo(data_source="today", field="year", label="올해 연도", example="2026"),
    FormFieldInfo(data_source="today", field="month", label="이번 달", example="03"),
    FormFieldInfo(data_source="today", field="day", label="오늘 일", example="24"),
    FormFieldInfo(data_source="today", field="weekday", label="오늘 요일", example="화요일"),
]


# ─── 셀 좌표 파서 ───

def parse_cell(cell_str: str) -> tuple[int, int]:
    m = re.match(r"([A-Z]+)(\d+)", cell_str.upper())
    if not m:
        raise ValueError(f"잘못된 셀 주소: {cell_str}")
    col = column_index_from_string(m.group(1))
    row = int(m.group(2))
    return row, col


# ─── 데이터 페처 ───

async def fetch_asset_data(asset_id: int, db: AsyncSession) -> dict:
    from app.models.asset import Asset
    from app.models.master import (
        GroupNode, LocationNode, EquipmentType,
        OsCatalog, AntivirusCatalog, Person, Department,
    )
    from sqlalchemy.orm import aliased

    Manager = aliased(Person)
    Supervisor = aliased(Person)
    MgrDept = aliased(Department)
    SupDept = aliased(Department)

    stmt = (
        select(
            Asset, GroupNode, LocationNode, EquipmentType,
            OsCatalog, AntivirusCatalog,
            Manager, Supervisor, MgrDept, SupDept,
        )
        .outerjoin(GroupNode, Asset.group_id == GroupNode.id)
        .outerjoin(LocationNode, Asset.location_id == LocationNode.id)
        .outerjoin(EquipmentType, Asset.equipment_type_id == EquipmentType.id)
        .outerjoin(OsCatalog, Asset.os_id == OsCatalog.id)
        .outerjoin(AntivirusCatalog, Asset.av_id == AntivirusCatalog.id)
        .outerjoin(Manager, Asset.manager_id == Manager.id)
        .outerjoin(Supervisor, Asset.supervisor_id == Supervisor.id)
        .outerjoin(MgrDept, Manager.dept_id == MgrDept.id)
        .outerjoin(SupDept, Supervisor.dept_id == SupDept.id)
        .where(Asset.id == asset_id)
    )
    row = (await db.execute(stmt)).first()
    if not row:
        return {}

    asset, group, loc, etype, os_, av, mgr, sup, mgr_dept, sup_dept = row
    return {
        "asset_code": asset.asset_code,
        "asset_name": asset.asset_name,
        "model_name": asset.model_name,
        "serial_number": asset.serial_number,
        "ip_address": asset.ip_address,
        "purpose": asset.purpose,
        "importance": asset.importance,
        "status": asset.status,
        "install_date": str(asset.install_date) if asset.install_date else "",
        "group_name": group.name if group else "",
        "group_full_path": group.full_path if group else "",
        "location_name": loc.name if loc else "",
        "location_full_path": loc.full_path if loc else "",
        "equipment_type_name": etype.name if etype else "",
        "os_name": os_.name if os_ else "",
        "os_version": os_.version if os_ else "",
        "av_name": av.name if av else "",
        "av_version": av.version if av else "",
        "manager_name": mgr.name if mgr else "",
        "manager_dept": mgr_dept.name if mgr_dept else "",
        "manager_title": mgr.title if mgr else "",
        "manager_contact": mgr.contact if mgr else "",
        "supervisor_name": sup.name if sup else "",
        "supervisor_dept": sup_dept.name if sup_dept else "",
        "supervisor_title": sup.title if sup else "",
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
            "hw_cpu": "AssetHwCpu", "hw_memory": "AssetHwMemory",
            "hw_disk": "AssetHwDisk", "hw_gpu": "AssetHwGpu", "hw_nic": "AssetHwNic",
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


# ─── 값 포맷팅 ───

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


# ─── 메인: 양식 보고서 생성 ───

async def generate_form_report(
    template_id: int,
    asset_id: int,
    db: AsyncSession,
) -> tuple[str, str]:
    template = await db.get(ReportFormTemplate, template_id)
    if not template:
        raise ValueError("양식을 찾을 수 없습니다")

    stmt = (
        select(ReportFormMapping)
        .where(ReportFormMapping.template_id == template_id)
        .order_by(ReportFormMapping.sort_order)
    )
    mappings = (await db.execute(stmt)).scalars().all()

    data_cache: dict = {}

    async def get_data(ds: str):
        if ds not in data_cache:
            data_cache[ds] = await fetch_data_source(ds, asset_id, db)
        return data_cache[ds]

    wb = load_workbook(template.file_path)
    ws = wb.active

    # 단건 매핑
    for m in mappings:
        if m.repeat_direction:
            continue
        row, col = parse_cell(m.cell)
        if m.data_source == "static":
            ws.cell(row, col).value = m.field
            continue
        data = await get_data(m.data_source)
        if isinstance(data, dict):
            ws.cell(row, col).value = format_value(data.get(m.field, ""), m.format)

    # 반복 매핑
    repeat_groups: dict = {}
    for m in mappings:
        if not m.repeat_direction:
            continue
        row, col = parse_cell(m.cell)
        key = (m.data_source, row)
        if key not in repeat_groups:
            repeat_groups[key] = []
        repeat_groups[key].append((m, row, col))

    for (ds, start_row), group in repeat_groups.items():
        data = await get_data(ds)
        if not isinstance(data, list):
            continue
        max_rows = group[0][0].repeat_max_rows or 50
        for i, item in enumerate(data[:max_rows]):
            for m, base_row, base_col in group:
                target_row = base_row + i
                value = item.get(m.field, "")
                ws.cell(target_row, base_col).value = format_value(value, m.format)
                if i > 0:
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
