from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists
from app.core.database import get_db
from app.schemas.master import LocationNodeCreate, LocationNodeRead, LocationNodeUpdate
from app.models.master import LocationNode
from app.models.asset import Asset

router = APIRouter()


async def _compute_full_path(db: AsyncSession, parent_id: int | None, name: str) -> str:
    if parent_id is None:
        return name
    parent = await db.get(LocationNode, parent_id)
    if not parent:
        raise HTTPException(404, "부모 위치를 찾을 수 없습니다")
    return f"{parent.full_path} > {name}"


async def _compute_depth(db: AsyncSession, parent_id: int | None) -> int:
    if parent_id is None:
        return 0
    parent = await db.get(LocationNode, parent_id)
    return (parent.depth + 1) if parent else 0


@router.get("", response_model=list[LocationNodeRead])
async def get_locations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LocationNode).order_by(LocationNode.depth, LocationNode.id))
    return result.scalars().all()


@router.post("", response_model=LocationNodeRead, status_code=201)
async def create_location(body: LocationNodeCreate, db: AsyncSession = Depends(get_db)):
    full_path = await _compute_full_path(db, body.parent_id, body.name)
    depth = await _compute_depth(db, body.parent_id)
    node = LocationNode(**body.model_dump(), full_path=full_path, depth=depth)
    db.add(node)
    await db.flush()
    await db.refresh(node)
    return node


@router.patch("/{node_id}", response_model=LocationNodeRead)
async def update_location(node_id: int, body: LocationNodeUpdate, db: AsyncSession = Depends(get_db)):
    node = await db.get(LocationNode, node_id)
    if not node:
        raise HTTPException(404, "위치 노드를 찾을 수 없습니다")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(node, k, v)
    if body.name is not None or body.parent_id is not None:
        node.full_path = await _compute_full_path(db, node.parent_id, node.name)
        node.depth = await _compute_depth(db, node.parent_id)
    await db.flush()
    await db.refresh(node)
    return node


@router.delete("/{node_id}", status_code=204)
async def delete_location(node_id: int, db: AsyncSession = Depends(get_db)):
    has_assets = await db.scalar(select(exists().where(Asset.location_id == node_id)))
    if has_assets:
        raise HTTPException(409, "이 위치에 등록된 자산이 있어 삭제할 수 없습니다")
    node = await db.get(LocationNode, node_id)
    if node:
        await db.delete(node)
