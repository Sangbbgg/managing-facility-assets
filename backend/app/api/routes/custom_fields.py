from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.schemas.custom_field import CustomFieldCreate, CustomFieldRead, CustomFieldUpdate
from app.models.custom_field import AssetCustomField

router = APIRouter()


@router.get("/{asset_id}/custom-fields", response_model=list[CustomFieldRead])
async def get_custom_fields(asset_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AssetCustomField)
        .where(AssetCustomField.asset_id == asset_id)
        .order_by(AssetCustomField.sort_order)
    )
    return result.scalars().all()


@router.post("/{asset_id}/custom-fields", response_model=CustomFieldRead, status_code=201)
async def create_custom_field(
    asset_id: int, body: CustomFieldCreate, db: AsyncSession = Depends(get_db),
):
    field = AssetCustomField(asset_id=asset_id, **body.model_dump())
    db.add(field)
    await db.flush()
    await db.refresh(field)
    return field


@router.patch("/{asset_id}/custom-fields/{field_id}", response_model=CustomFieldRead)
async def update_custom_field(
    asset_id: int, field_id: int, body: CustomFieldUpdate,
    db: AsyncSession = Depends(get_db),
):
    field = await db.get(AssetCustomField, field_id)
    if not field or field.asset_id != asset_id:
        raise HTTPException(404, "메모를 찾을 수 없습니다")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(field, k, v)
    return field


@router.delete("/{asset_id}/custom-fields/{field_id}", status_code=204)
async def delete_custom_field(
    asset_id: int, field_id: int, db: AsyncSession = Depends(get_db),
):
    field = await db.get(AssetCustomField, field_id)
    if field and field.asset_id == asset_id:
        await db.delete(field)


@router.patch("/{asset_id}/custom-fields/reorder")
async def reorder_custom_fields(
    asset_id: int, order: list[int], db: AsyncSession = Depends(get_db),
):
    for idx, field_id in enumerate(order):
        field = await db.get(AssetCustomField, field_id)
        if field and field.asset_id == asset_id:
            field.sort_order = idx
    return {"ok": True}
