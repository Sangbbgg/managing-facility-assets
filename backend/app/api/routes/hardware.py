from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.hw_info import (
    AssetHwSystem, AssetHwCpu, AssetHwMemory,
    AssetHwDisk, AssetHwGpu, AssetHwNic,
)
from app.schemas.hw_info import (
    HwSystemRead, HwCpuRead, HwMemoryRead,
    HwDiskRead, HwGpuRead, HwNicRead, HwAllRead,
)

router = APIRouter()

HW_MODEL_MAP = {
    "systems":  (AssetHwSystem,  HwSystemRead),
    "cpus":     (AssetHwCpu,     HwCpuRead),
    "memories": (AssetHwMemory,  HwMemoryRead),
    "disks":    (AssetHwDisk,    HwDiskRead),
    "gpus":     (AssetHwGpu,     HwGpuRead),
    "nics":     (AssetHwNic,     HwNicRead),
}


def _get_model(hw_type: str):
    entry = HW_MODEL_MAP.get(hw_type)
    if not entry:
        raise HTTPException(400, f"지원하지 않는 HW 유형: {hw_type}. 가능한 값: {list(HW_MODEL_MAP.keys())}")
    return entry


@router.get("/{asset_id}/hardware", response_model=HwAllRead)
async def get_all_hardware(asset_id: int, db: AsyncSession = Depends(get_db)):
    result = {}
    for key, (model, _) in HW_MODEL_MAP.items():
        rows = await db.execute(
            select(model).where(model.asset_id == asset_id).order_by(model.collected_at.desc())
        )
        result[key] = rows.scalars().all()
    return result


@router.get("/{asset_id}/hardware/{hw_type}")
async def get_hardware_by_type(
    asset_id: int,
    hw_type: str = Path(...),
    db: AsyncSession = Depends(get_db),
):
    model, schema = _get_model(hw_type)
    rows = await db.execute(
        select(model).where(model.asset_id == asset_id).order_by(model.collected_at.desc())
    )
    return rows.scalars().all()


@router.delete("/{asset_id}/hardware/{hw_type}/{hw_id}", status_code=204)
async def delete_hardware(
    asset_id: int,
    hw_type: str,
    hw_id: int,
    db: AsyncSession = Depends(get_db),
):
    model, _ = _get_model(hw_type)
    item = await db.get(model, hw_id)
    if item and item.asset_id == asset_id:
        await db.delete(item)
