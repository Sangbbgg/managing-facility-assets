from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.core.database import get_db
from app.schemas.layout import LayoutCreate, LayoutRead, LayoutUpdate
from app.models.layout import ColumnLayout

router = APIRouter()


@router.get("", response_model=list[LayoutRead])
async def get_layouts(
    page_key: str = Query("asset_list"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ColumnLayout)
        .where(ColumnLayout.page_key == page_key)
        .order_by(ColumnLayout.is_default.desc(), ColumnLayout.name)
    )
    return result.scalars().all()


@router.post("", response_model=LayoutRead, status_code=201)
async def create_layout(body: LayoutCreate, db: AsyncSession = Depends(get_db)):
    layout = ColumnLayout(**body.model_dump())
    db.add(layout)
    await db.flush()
    await db.refresh(layout)
    return layout


@router.patch("/{layout_id}", response_model=LayoutRead)
async def update_layout(layout_id: int, body: LayoutUpdate, db: AsyncSession = Depends(get_db)):
    layout = await db.get(ColumnLayout, layout_id)
    if not layout:
        raise HTTPException(404, "레이아웃을 찾을 수 없습니다")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(layout, k, v)
    return layout


@router.delete("/{layout_id}", status_code=204)
async def delete_layout(layout_id: int, db: AsyncSession = Depends(get_db)):
    layout = await db.get(ColumnLayout, layout_id)
    if layout:
        await db.delete(layout)


@router.patch("/{layout_id}/default", response_model=LayoutRead)
async def set_default_layout(layout_id: int, db: AsyncSession = Depends(get_db)):
    layout = await db.get(ColumnLayout, layout_id)
    if not layout:
        raise HTTPException(404, "레이아웃을 찾을 수 없습니다")
    await db.execute(
        update(ColumnLayout)
        .where(ColumnLayout.page_key == layout.page_key)
        .values(is_default=False)
    )
    layout.is_default = True
    return layout
