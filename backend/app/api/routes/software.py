from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.sw_info import AssetSwAccount, AssetSwHotfix, AssetSwProcess, AssetSwProduct
from app.models.collection import AssetNetworkConnection
from app.schemas.sw_info import (
    AccountStatusUpdate,
    SwAllRead,
    SwAccountRead,
    SwConnectionRead,
    SwHotfixRead,
    SwProcessRead,
    SwProductRead,
)

router = APIRouter()

SW_MODEL_MAP = {
    "products":  (AssetSwProduct,  SwProductRead),
    "hotfixes":  (AssetSwHotfix,   SwHotfixRead),
    "processes": (AssetSwProcess,  SwProcessRead),
    "accounts": (AssetSwAccount, SwAccountRead),
    "connections": (AssetNetworkConnection, SwConnectionRead),
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


@router.patch("/{asset_id}/software/accounts/status")
async def update_account_statuses(
    asset_id: int,
    body: AccountStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    rows = (
        await db.execute(
            select(AssetSwAccount).where(AssetSwAccount.asset_id == asset_id)
        )
    ).scalars().all()

    disabled_ids = set(body.disabled_account_ids or [])
    for row in rows:
        row.enabled = row.id not in disabled_ids

    return {"status": "ok", "updated_count": len(rows)}
