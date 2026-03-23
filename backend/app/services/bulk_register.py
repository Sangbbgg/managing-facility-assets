import io
import tempfile
from fastapi import UploadFile
from openpyxl import Workbook, load_workbook
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services.asset_code import issue_asset_code
from app.models.master import GroupNode, EquipmentType
from app.models.asset import Asset

TEMPLATE_HEADERS = [
    "자산명*", "그룹코드*", "장비종류코드*",
    "위치ID", "담당자ID", "중요도(상/중/하)", "설치일(YYYY-MM-DD)", "IP주소", "용도"
]


def generate_template() -> str:
    wb = Workbook()
    ws = wb.active
    ws.title = "자산등록"
    for col, header in enumerate(TEMPLATE_HEADERS, 1):
        ws.cell(1, col, header)
    ws.cell(2, 1, "예시_서버01")
    ws.cell(2, 2, "GT1")
    ws.cell(2, 3, "SER")
    ws.cell(2, 6, "중")
    tmp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
    wb.save(tmp.name)
    return tmp.name


async def parse_and_register(file: UploadFile, db: AsyncSession) -> dict:
    content = await file.read()
    wb = load_workbook(io.BytesIO(content))
    ws = wb.active

    results = {"success": 0, "errors": []}

    for row_idx in range(2, ws.max_row + 1):
        try:
            asset_name   = ws.cell(row_idx, 1).value
            group_code   = ws.cell(row_idx, 2).value
            type_code    = ws.cell(row_idx, 3).value
            location_id  = ws.cell(row_idx, 4).value
            manager_id   = ws.cell(row_idx, 5).value
            importance   = ws.cell(row_idx, 6).value or "중"
            install_date = ws.cell(row_idx, 7).value
            ip_address   = ws.cell(row_idx, 8).value
            purpose      = ws.cell(row_idx, 9).value

            if not asset_name or not group_code or not type_code:
                if not asset_name and not group_code and not type_code:
                    break  # 빈 행이면 종료
                results["errors"].append({"row": row_idx, "error": "자산명·그룹코드·장비종류코드는 필수입니다"})
                continue

            # 그룹·장비종류 존재 확인
            group = await db.scalar(select(GroupNode).where(GroupNode.code == str(group_code)))
            etype = await db.scalar(select(EquipmentType).where(EquipmentType.code == str(type_code)))
            if not group:
                results["errors"].append({"row": row_idx, "error": f"그룹코드 '{group_code}' 없음"})
                continue
            if not etype:
                results["errors"].append({"row": row_idx, "error": f"장비종류코드 '{type_code}' 없음"})
                continue

            asset_code = await issue_asset_code(db, str(group_code), str(type_code))

            asset = Asset(
                asset_code=asset_code,
                asset_name=str(asset_name),
                group_id=group.id,
                equipment_type_id=etype.id,
                location_id=int(location_id) if location_id else None,
                manager_id=int(manager_id) if manager_id else None,
                importance=str(importance) if importance else "중",
                install_date=install_date if hasattr(install_date, 'year') else None,
                ip_address=str(ip_address) if ip_address else None,
                purpose=str(purpose) if purpose else None,
            )
            db.add(asset)
            await db.flush()
            results["success"] += 1

        except Exception as e:
            results["errors"].append({"row": row_idx, "error": str(e)})

    return results
