from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.schemas.master import (
    EquipmentTypeCreate, EquipmentTypeRead, EquipmentTypeUpdate,
    OsCatalogCreate, OsCatalogRead, OsCatalogUpdate,
    AntivirusCatalogCreate, AntivirusCatalogRead, AntivirusCatalogUpdate,
)
from app.models.master import EquipmentType, OsCatalog, AntivirusCatalog

router = APIRouter()


# ── Equipment Types ───────────────────────────────────────────

@router.get("/equipment-types", response_model=list[EquipmentTypeRead])
async def get_equipment_types(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EquipmentType).order_by(EquipmentType.id))
    return result.scalars().all()


@router.post("/equipment-types", response_model=EquipmentTypeRead, status_code=201)
async def create_equipment_type(body: EquipmentTypeCreate, db: AsyncSession = Depends(get_db)):
    row = EquipmentType(**body.model_dump())
    db.add(row)
    await db.flush()
    await db.refresh(row)
    return row


@router.patch("/equipment-types/{type_id}", response_model=EquipmentTypeRead)
async def update_equipment_type(type_id: int, body: EquipmentTypeUpdate, db: AsyncSession = Depends(get_db)):
    row = await db.get(EquipmentType, type_id)
    if not row:
        raise HTTPException(404, "장비 종류를 찾을 수 없습니다")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    await db.flush()
    await db.refresh(row)
    return row


@router.delete("/equipment-types/{type_id}", status_code=204)
async def delete_equipment_type(type_id: int, db: AsyncSession = Depends(get_db)):
    row = await db.get(EquipmentType, type_id)
    if row:
        await db.delete(row)


# ── OS Catalog ────────────────────────────────────────────────

@router.get("/os", response_model=list[OsCatalogRead])
async def get_os_list(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OsCatalog).order_by(OsCatalog.id))
    return result.scalars().all()


@router.post("/os", response_model=OsCatalogRead, status_code=201)
async def create_os(body: OsCatalogCreate, db: AsyncSession = Depends(get_db)):
    row = OsCatalog(**body.model_dump())
    db.add(row)
    await db.flush()
    await db.refresh(row)
    return row


@router.patch("/os/{os_id}", response_model=OsCatalogRead)
async def update_os(os_id: int, body: OsCatalogUpdate, db: AsyncSession = Depends(get_db)):
    row = await db.get(OsCatalog, os_id)
    if not row:
        raise HTTPException(404, "OS 카탈로그를 찾을 수 없습니다")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    await db.flush()
    await db.refresh(row)
    return row


@router.delete("/os/{os_id}", status_code=204)
async def delete_os(os_id: int, db: AsyncSession = Depends(get_db)):
    row = await db.get(OsCatalog, os_id)
    if row:
        await db.delete(row)


# ── Antivirus Catalog ─────────────────────────────────────────

@router.get("/av", response_model=list[AntivirusCatalogRead])
async def get_av_list(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AntivirusCatalog).order_by(AntivirusCatalog.id))
    return result.scalars().all()


@router.post("/av", response_model=AntivirusCatalogRead, status_code=201)
async def create_av(body: AntivirusCatalogCreate, db: AsyncSession = Depends(get_db)):
    row = AntivirusCatalog(**body.model_dump())
    db.add(row)
    await db.flush()
    await db.refresh(row)
    return row


@router.patch("/av/{av_id}", response_model=AntivirusCatalogRead)
async def update_av(av_id: int, body: AntivirusCatalogUpdate, db: AsyncSession = Depends(get_db)):
    row = await db.get(AntivirusCatalog, av_id)
    if not row:
        raise HTTPException(404, "백신 카탈로그를 찾을 수 없습니다")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    await db.flush()
    await db.refresh(row)
    return row


@router.delete("/av/{av_id}", status_code=204)
async def delete_av(av_id: int, db: AsyncSession = Depends(get_db)):
    row = await db.get(AntivirusCatalog, av_id)
    if row:
        await db.delete(row)
