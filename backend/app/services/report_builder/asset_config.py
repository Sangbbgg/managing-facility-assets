import tempfile
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from openpyxl import Workbook
from app.models.asset import Asset
from app.models.master import GroupNode, LocationNode, EquipmentType, OsCatalog, AntivirusCatalog
from ._common import write_header, style_data_row

HEADERS = ["자산코드", "설비명", "그룹", "위치", "장비종류", "OS", "백신", "IP", "시리얼", "중요도", "설치일", "상태"]
WIDTHS  = [18, 20, 20, 20, 12, 22, 22, 16, 18, 8, 12, 10]


async def build(date_from: date, date_to: date, db: AsyncSession) -> str:
    stmt = select(Asset).where(Asset.is_deleted == False).order_by(Asset.asset_code)
    assets = (await db.execute(stmt)).scalars().all()

    # 참조 테이블 일괄 로드
    groups   = {r.id: r for r in (await db.execute(select(GroupNode))).scalars()}
    locs     = {r.id: r for r in (await db.execute(select(LocationNode))).scalars()}
    eq_types = {r.id: r for r in (await db.execute(select(EquipmentType))).scalars()}
    os_map   = {r.id: r for r in (await db.execute(select(OsCatalog))).scalars()}
    av_map   = {r.id: r for r in (await db.execute(select(AntivirusCatalog))).scalars()}

    wb = Workbook()
    ws = wb.active
    ws.title = "형상관리대장"
    write_header(ws, HEADERS, WIDTHS)

    for i, a in enumerate(assets, 2):
        ws.cell(i, 1, a.asset_code)
        ws.cell(i, 2, a.asset_name)
        ws.cell(i, 3, groups[a.group_id].name if a.group_id and a.group_id in groups else "")
        ws.cell(i, 4, locs[a.location_id].full_path if a.location_id and a.location_id in locs else "")
        ws.cell(i, 5, eq_types[a.equipment_type_id].name if a.equipment_type_id and a.equipment_type_id in eq_types else "")
        ws.cell(i, 6, os_map[a.os_id].name if a.os_id and a.os_id in os_map else "")
        ws.cell(i, 7, av_map[a.av_id].name if a.av_id and a.av_id in av_map else "")
        ws.cell(i, 8, a.ip_address or "")
        ws.cell(i, 9, a.serial_number or "")
        ws.cell(i, 10, a.importance or "")
        ws.cell(i, 11, str(a.install_date) if a.install_date else "")
        ws.cell(i, 12, a.status)
        style_data_row(ws, i, len(HEADERS))

    tmp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
    wb.save(tmp.name)
    return tmp.name
