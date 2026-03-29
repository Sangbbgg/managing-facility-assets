from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.asset import Asset
from app.models.custom_field import AssetCustomField
from app.schemas.custom_field import (
    CustomFieldCreate,
    CustomFieldKeyCreate,
    CustomFieldRead,
    CustomFieldUpdate,
    CustomFieldValueUpsert,
)

router = APIRouter()


async def _sync_asset_custom_fields_json(asset_id: int, db: AsyncSession) -> None:
    asset = await db.get(Asset, asset_id)
    if not asset:
        return

    rows = (
        await db.execute(
            select(AssetCustomField)
            .where(AssetCustomField.asset_id == asset_id)
            .order_by(AssetCustomField.sort_order, AssetCustomField.id)
        )
    ).scalars().all()

    asset.custom_fields_json = {
        row.field_key: row.field_value
        for row in rows
        if row.field_key is not None and str(row.field_key).strip()
    }


async def _find_or_create_field(asset_id: int, field_key: str, db: AsyncSession) -> AssetCustomField:
    normalized_key = field_key.strip()
    if not normalized_key:
        raise HTTPException(400, "키를 입력해주세요")

    existing = (
        await db.execute(
            select(AssetCustomField)
            .where(
                AssetCustomField.asset_id == asset_id,
                AssetCustomField.field_key == normalized_key,
            )
            .limit(1)
        )
    ).scalar_one_or_none()
    if existing:
        return existing

    sort_order = (
        await db.execute(
            select(AssetCustomField)
            .where(AssetCustomField.asset_id == asset_id)
            .order_by(AssetCustomField.sort_order.desc(), AssetCustomField.id.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    next_order = (sort_order.sort_order + 1) if sort_order else 0

    field = AssetCustomField(
        asset_id=asset_id,
        field_key=normalized_key,
        field_value="",
        sort_order=next_order,
    )
    db.add(field)
    await db.flush()
    return field


@router.get("/custom-fields/keys")
async def get_custom_field_keys(db: AsyncSession = Depends(get_db)):
    rows = (
        await db.execute(
            select(AssetCustomField.field_key)
            .distinct()
            .order_by(AssetCustomField.field_key.asc())
        )
    ).scalars().all()
    return [row for row in rows if row and str(row).strip()]


@router.post("/custom-fields/keys", status_code=201)
async def create_custom_field_key(body: CustomFieldKeyCreate, db: AsyncSession = Depends(get_db)):
    field_key = body.field_key.strip()
    if not field_key:
        raise HTTPException(400, "키를 입력해주세요")

    assets = (
        await db.execute(
            select(Asset).where(Asset.is_deleted == False).order_by(Asset.id)
        )
    ).scalars().all()

    created_count = 0
    for asset in assets:
        existing = (
            await db.execute(
                select(AssetCustomField)
                .where(
                    AssetCustomField.asset_id == asset.id,
                    AssetCustomField.field_key == field_key,
                )
                .limit(1)
            )
        ).scalar_one_or_none()
        if existing:
            continue

        last_field = (
            await db.execute(
                select(AssetCustomField)
                .where(AssetCustomField.asset_id == asset.id)
                .order_by(AssetCustomField.sort_order.desc(), AssetCustomField.id.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        next_order = (last_field.sort_order + 1) if last_field else 0

        db.add(
            AssetCustomField(
                asset_id=asset.id,
                field_key=field_key,
                field_value="",
                sort_order=next_order,
            )
        )
        created_count += 1

    await db.flush()
    for asset in assets:
        await _sync_asset_custom_fields_json(asset.id, db)

    return {"field_key": field_key, "created_count": created_count}


@router.delete("/custom-fields/keys/{field_key}", status_code=204)
async def delete_custom_field_key(field_key: str, db: AsyncSession = Depends(get_db)):
    rows = (
        await db.execute(
            select(AssetCustomField).where(AssetCustomField.field_key == field_key)
        )
    ).scalars().all()

    affected_asset_ids = sorted({row.asset_id for row in rows})
    for row in rows:
        await db.delete(row)

    await db.flush()
    for asset_id in affected_asset_ids:
        await _sync_asset_custom_fields_json(asset_id, db)


@router.get("/{asset_id}/custom-fields", response_model=list[CustomFieldRead])
async def get_custom_fields(asset_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AssetCustomField)
        .where(AssetCustomField.asset_id == asset_id)
        .order_by(AssetCustomField.sort_order, AssetCustomField.id)
    )
    return result.scalars().all()


@router.post("/{asset_id}/custom-fields", response_model=CustomFieldRead, status_code=201)
async def create_custom_field(
    asset_id: int,
    body: CustomFieldCreate,
    db: AsyncSession = Depends(get_db),
):
    field = AssetCustomField(asset_id=asset_id, **body.model_dump())
    db.add(field)
    await db.flush()
    await _sync_asset_custom_fields_json(asset_id, db)
    await db.flush()
    await db.refresh(field)
    return field


@router.put("/{asset_id}/custom-fields/by-key/{field_key}", response_model=CustomFieldRead)
async def upsert_custom_field_by_key(
    asset_id: int,
    field_key: str,
    body: CustomFieldValueUpsert,
    db: AsyncSession = Depends(get_db),
):
    field = await _find_or_create_field(asset_id, field_key, db)
    field.field_value = body.field_value
    await db.flush()
    await _sync_asset_custom_fields_json(asset_id, db)
    await db.flush()
    await db.refresh(field)
    return field


@router.patch("/{asset_id}/custom-fields/{field_id}", response_model=CustomFieldRead)
async def update_custom_field(
    asset_id: int,
    field_id: int,
    body: CustomFieldUpdate,
    db: AsyncSession = Depends(get_db),
):
    field = await db.get(AssetCustomField, field_id)
    if not field or field.asset_id != asset_id:
        raise HTTPException(404, "메모를 찾을 수 없습니다")

    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(field, key, value)

    await db.flush()
    await _sync_asset_custom_fields_json(asset_id, db)
    await db.flush()
    return field


@router.delete("/{asset_id}/custom-fields/{field_id}", status_code=204)
async def delete_custom_field(
    asset_id: int,
    field_id: int,
    db: AsyncSession = Depends(get_db),
):
    field = await db.get(AssetCustomField, field_id)
    if field and field.asset_id == asset_id:
        await db.delete(field)
        await db.flush()
        await _sync_asset_custom_fields_json(asset_id, db)


@router.patch("/{asset_id}/custom-fields/reorder")
async def reorder_custom_fields(
    asset_id: int,
    order: list[int],
    db: AsyncSession = Depends(get_db),
):
    for idx, field_id in enumerate(order):
        field = await db.get(AssetCustomField, field_id)
        if field and field.asset_id == asset_id:
            field.sort_order = idx

    await db.flush()
    await _sync_asset_custom_fields_json(asset_id, db)
    return {"ok": True}
