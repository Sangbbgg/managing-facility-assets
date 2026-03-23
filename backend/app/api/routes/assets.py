from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.schemas.asset import AssetCreate, AssetRead, AssetUpdate
from app.models.asset import Asset
from app.models.master import GroupNode, EquipmentType
from app.services.asset_code import issue_asset_code

router = APIRouter()


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
    result = await db.execute(stmt.order_by(Asset.id))
    return result.scalars().all()


@router.get("/{asset_id}", response_model=AssetRead)
async def get_asset(asset_id: int, db: AsyncSession = Depends(get_db)):
    asset = await db.get(Asset, asset_id)
    if not asset or asset.is_deleted:
        raise HTTPException(404, "자산을 찾을 수 없습니다")
    return asset


@router.post("", response_model=AssetRead, status_code=201)
async def create_asset(body: AssetCreate, db: AsyncSession = Depends(get_db)):
    group = await db.get(GroupNode, body.group_id)
    if not group or not group.code:
        raise HTTPException(400, "code가 있는 그룹 노드만 자산 등록 가능합니다")
    eq_type = await db.get(EquipmentType, body.equipment_type_id)
    if not eq_type:
        raise HTTPException(400, "존재하지 않는 장비 종류입니다")
    asset_code = await issue_asset_code(db, group.code, eq_type.code)
    asset = Asset(**body.model_dump(), asset_code=asset_code, is_deleted=False)
    db.add(asset)
    await db.flush()
    await db.refresh(asset)
    return asset


@router.patch("/{asset_id}", response_model=AssetRead)
async def update_asset(asset_id: int, body: AssetUpdate, db: AsyncSession = Depends(get_db)):
    asset = await db.get(Asset, asset_id)
    if not asset or asset.is_deleted:
        raise HTTPException(404, "자산을 찾을 수 없습니다")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(asset, k, v)
    await db.flush()
    await db.refresh(asset)
    return asset


@router.delete("/{asset_id}", status_code=204)
async def delete_asset(asset_id: int, db: AsyncSession = Depends(get_db)):
    asset = await db.get(Asset, asset_id)
    if not asset or asset.is_deleted:
        raise HTTPException(404, "자산을 찾을 수 없습니다")
    asset.is_deleted = True
