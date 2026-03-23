from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.sw_info import AssetSwProduct, AssetSwHotfix, AssetSwProcess
from app.schemas.sw_info import SwProductRead, SwHotfixRead, SwProcessRead, SwAllRead

router = APIRouter()

SW_MODEL_MAP = {
    "products":  (AssetSwProduct,  SwProductRead),
    "hotfixes":  (AssetSwHotfix,   SwHotfixRead),
    "processes": (AssetSwProcess,  SwProcessRead),
}


def _get_model(sw_type: str):
    entry = SW_MODEL_MAP.get(sw_type)
    if not entry:
        raise HTTPException(400, f"지원하지 않는 SW 유형: {sw_type}. 가능한 값: {list(SW_MODEL_MAP.keys())}")
    return entry


@router.get("/{asset_id}/software", response_model=SwAllRead)
async def get_all_software(asset_id: int, db: AsyncSession = Depends(get_db)):
    result = {}
    for key, (model, _) in SW_MODEL_MAP.items():
        rows = await db.execute(
            select(model).where(model.asset_id == asset_id).order_by(model.collected_at.desc())
        )
        result[key] = rows.scalars().all()
    return result


@router.get("/{asset_id}/software/{sw_type}")
async def get_software_by_type(
    asset_id: int,
    sw_type: str = Path(...),
    db: AsyncSession = Depends(get_db),
):
    model, _ = _get_model(sw_type)
    rows = await db.execute(
        select(model).where(model.asset_id == asset_id).order_by(model.collected_at.desc())
    )
    return rows.scalars().all()


@router.delete("/{asset_id}/software/{sw_type}/{sw_id}", status_code=204)
async def delete_software(
    asset_id: int,
    sw_type: str,
    sw_id: int,
    db: AsyncSession = Depends(get_db),
):
    model, _ = _get_model(sw_type)
    item = await db.get(model, sw_id)
    if item and item.asset_id == asset_id:
        await db.delete(item)
