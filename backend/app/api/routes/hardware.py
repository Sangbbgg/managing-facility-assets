from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.hw_info import (
    AssetHwSystem, AssetHwCpu, AssetHwMemory,
    AssetHwDisk, AssetHwOptical, AssetHwGpu, AssetHwNic,
)
from app.schemas.hw_info import (
    HwSystemRead, HwCpuRead, HwMemoryRead,
    HwDiskRead, HwOpticalRead, HwGpuRead, HwNicRead, HwAllRead, UnusedNicUpdate,
)
from app.models.asset import Asset

router = APIRouter()

HW_MODEL_MAP = {
    "systems":  (AssetHwSystem,  HwSystemRead),
    "cpus":     (AssetHwCpu,     HwCpuRead),
    "memories": (AssetHwMemory,  HwMemoryRead),
    "disks":    (AssetHwDisk,    HwDiskRead),
    "opticals": (AssetHwOptical, HwOpticalRead),
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


@router.patch("/{asset_id}/hardware/nics/unused")
async def update_unused_nics(
    asset_id: int,
    body: UnusedNicUpdate,
    db: AsyncSession = Depends(get_db),
):
    asset = await db.get(Asset, asset_id)
    if not asset or asset.is_deleted:
        raise HTTPException(404, "자산을 찾을 수 없습니다")

    rows = await db.execute(select(AssetHwNic).where(AssetHwNic.asset_id == asset_id))
    nics = rows.scalars().all()
    nic_map = {nic.id: nic for nic in nics}

    requested_ids = {
        nic_id
        for nic_id in body.nic_ids
        if nic_id in nic_map and nic_id != asset.representative_nic_id
    }

    for nic in nics:
        nic.is_unused = nic.id in requested_ids

    await db.flush()
    return {"asset_id": asset_id, "unused_nic_ids": sorted(requested_ids)}
