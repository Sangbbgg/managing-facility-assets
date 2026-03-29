from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.asset import Asset, AssetChangeLog
from app.models.hw_info import AssetHwNic
from app.models.master import EquipmentType, GroupNode
from app.models.sw_info import AssetSwAccount
from app.schemas.asset import AssetCreate, AssetDetailListItem, AssetRead, AssetUpdate
from app.services.asset_code import issue_asset_code, preview_asset_code as preview_next_asset_code
from app.services.asset_manager_assignment import assign_asset_manager_if_missing

router = APIRouter()


async def _serialize_asset(db: AsyncSession, asset: Asset) -> dict:
    ip_address = None
    representative_account_name = None
    if asset.representative_nic_id:
        nic = await db.get(AssetHwNic, asset.representative_nic_id)
        if nic and nic.asset_id == asset.id:
            ip_address = nic.ipv4_address
    if asset.representative_account_id:
        account = await db.get(AssetSwAccount, asset.representative_account_id)
        if account and account.asset_id == asset.id:
            representative_account_name = account.account_name

    return {
        "id": asset.id,
        "asset_code": asset.asset_code,
        "asset_name": asset.asset_name,
        "purpose": asset.purpose,
        "importance": asset.importance,
        "install_date": asset.install_date,
        "ip_address": ip_address,
        "representative_nic_id": asset.representative_nic_id,
        "representative_account_id": asset.representative_account_id,
        "representative_account_name": representative_account_name,
        "status": asset.status,
        "is_deleted": asset.is_deleted,
        "created_at": asset.created_at,
        "updated_at": asset.updated_at,
        "group_id": asset.group_id,
        "location_id": asset.location_id,
        "equipment_type_id": asset.equipment_type_id,
        "manager_id": asset.manager_id,
        "last_collected_at": asset.last_collected_at,
        "custom_fields_json": asset.custom_fields_json,
    }


@router.get("/preview-code")
async def preview_asset_code(
    group_id: int = Query(...),
    type_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    group = await db.get(GroupNode, group_id)
    etype = await db.get(EquipmentType, type_id)
    if not group or not group.code:
        raise HTTPException(400, "코드가 있는 그룹 노드를 선택해주세요")
    if not etype:
        raise HTTPException(400, "존재하지 않는 장비 종류입니다")

    sequence_group_code = group.display_code or group.code
    display_group_code = group.display_code or group.code
    preview, next_seq = await preview_next_asset_code(
        db,
        sequence_group_code,
        display_group_code,
        etype.code,
    )
    return {
        "preview_code": preview,
        "group_code": display_group_code,
        "sequence_group_code": sequence_group_code,
        "type_code": etype.code,
        "next_seq": next_seq,
    }


@router.get("/bulk-template")
async def download_bulk_template(db: AsyncSession = Depends(get_db)):
    from app.services.bulk_register import generate_template

    file_path = await generate_template(db)
    return FileResponse(
        path=file_path,
        filename="자산_대량등록_템플릿.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.post("/bulk-register")
async def bulk_register(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    from app.services.bulk_register import parse_and_register

    return await parse_and_register(file, db)


@router.get("/enriched")
async def get_enriched_assets(db: AsyncSession = Depends(get_db)):
    from app.services.report_builder.data_fetchers import fetch_asset_rows

    return await fetch_asset_rows(0, None, db)


@router.get("/detail-list", response_model=list[AssetDetailListItem])
async def get_asset_detail_list(db: AsyncSession = Depends(get_db)):
    from app.services.asset_detail_list import fetch_asset_detail_list

    return await fetch_asset_detail_list(db)


@router.get("", response_model=list[AssetRead])
async def get_assets(
    group_id: int | None = Query(None),
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Asset).where(Asset.is_deleted == False)
    if group_id:
        stmt = stmt.where(Asset.group_id == group_id)
    if status:
        stmt = stmt.where(Asset.status == status)

    assets = (await db.execute(stmt.order_by(Asset.id))).scalars().all()
    return [await _serialize_asset(db, asset) for asset in assets]


@router.post("", response_model=AssetRead, status_code=201)
async def create_asset(body: AssetCreate, db: AsyncSession = Depends(get_db)):
    group = await db.get(GroupNode, body.group_id)
    if not group or not group.code:
        raise HTTPException(400, "코드가 있는 그룹 노드만 자산 등록 가능합니다")

    eq_type = await db.get(EquipmentType, body.equipment_type_id)
    if not eq_type:
        raise HTTPException(400, "존재하지 않는 장비 종류입니다")

    if body.representative_nic_id:
        nic = await db.get(AssetHwNic, body.representative_nic_id)
        if not nic:
            raise HTTPException(400, "존재하지 않는 대표 NIC입니다")
    if body.representative_account_id:
        account = await db.get(AssetSwAccount, body.representative_account_id)
        if not account:
            raise HTTPException(400, "존재하지 않는 대표 계정입니다")

    sequence_group_code = group.display_code or group.code
    display_group_code = group.display_code or group.code
    asset_code = await issue_asset_code(db, sequence_group_code, display_group_code, eq_type.code)
    asset = Asset(**body.model_dump(), asset_code=asset_code, is_deleted=False)
    await assign_asset_manager_if_missing(db, asset)
    db.add(asset)
    await db.flush()
    await db.refresh(asset)
    return await _serialize_asset(db, asset)


@router.get("/{asset_id}", response_model=AssetRead)
async def get_asset(asset_id: int, db: AsyncSession = Depends(get_db)):
    asset = await db.get(Asset, asset_id)
    if not asset or asset.is_deleted:
        raise HTTPException(404, "자산을 찾을 수 없습니다")
    return await _serialize_asset(db, asset)


@router.patch("/{asset_id}", response_model=AssetRead)
async def update_asset(asset_id: int, body: AssetUpdate, db: AsyncSession = Depends(get_db)):
    asset = await db.get(Asset, asset_id)
    if not asset or asset.is_deleted:
        raise HTTPException(404, "자산을 찾을 수 없습니다")

    old_data = {k: getattr(asset, k) for k in body.model_dump(exclude_unset=True)}
    new_data = body.model_dump(exclude_unset=True)

    for key, value in new_data.items():
        setattr(asset, key, value)

    if "representative_nic_id" in new_data and asset.representative_nic_id:
        nic = await db.get(AssetHwNic, asset.representative_nic_id)
        if not nic or nic.asset_id != asset.id:
            asset.representative_nic_id = None
        else:
            nic.is_unused = False

    if "representative_account_id" in new_data and asset.representative_account_id:
        account = await db.get(AssetSwAccount, asset.representative_account_id)
        if not account or account.asset_id != asset.id:
            asset.representative_account_id = None
        else:
            account.enabled = True

    await assign_asset_manager_if_missing(db, asset)
    await db.flush()

    from app.services.change_logger import log_changes

    await log_changes(
        db=db,
        asset_id=asset_id,
        changed_by="system",
        old_data={k: str(v) if v is not None else None for k, v in old_data.items()},
        new_data={k: str(v) if v is not None else None for k, v in new_data.items()},
    )

    await db.refresh(asset)
    return await _serialize_asset(db, asset)


@router.delete("/{asset_id}", status_code=204)
async def delete_asset(asset_id: int, db: AsyncSession = Depends(get_db)):
    asset = await db.get(Asset, asset_id)
    if not asset or asset.is_deleted:
        raise HTTPException(404, "자산을 찾을 수 없습니다")
    asset.is_deleted = True


@router.get("/{asset_id}/change-log")
async def get_change_log(asset_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AssetChangeLog)
        .where(AssetChangeLog.asset_id == asset_id)
        .order_by(AssetChangeLog.changed_at.desc())
    )
    return result.scalars().all()
