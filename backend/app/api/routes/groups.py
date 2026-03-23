from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists
from app.core.database import get_db
from app.schemas.master import GroupNodeCreate, GroupNodeRead, GroupNodeUpdate
from app.models.master import GroupNode
from app.models.asset import Asset

router = APIRouter()


async def _compute_full_path(db: AsyncSession, parent_id: int | None, name: str) -> str:
    if parent_id is None:
        return name
    parent = await db.get(GroupNode, parent_id)
    if not parent:
        raise HTTPException(404, "부모 그룹을 찾을 수 없습니다")
    return f"{parent.full_path} > {name}"


async def _compute_depth(db: AsyncSession, parent_id: int | None) -> int:
    if parent_id is None:
        return 0
    parent = await db.get(GroupNode, parent_id)
    return (parent.depth + 1) if parent else 0


@router.get("", response_model=list[GroupNodeRead])
async def get_groups(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GroupNode).order_by(GroupNode.depth, GroupNode.id))
    return result.scalars().all()


@router.get("/codeable", response_model=list[GroupNodeRead])
async def get_codeable_groups(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(GroupNode).where(GroupNode.code.isnot(None)).order_by(GroupNode.id)
    )
    return result.scalars().all()


@router.post("", response_model=GroupNodeRead, status_code=201)
async def create_group(body: GroupNodeCreate, db: AsyncSession = Depends(get_db)):
    full_path = await _compute_full_path(db, body.parent_id, body.name)
    depth = await _compute_depth(db, body.parent_id)
    node = GroupNode(**body.model_dump(), full_path=full_path, depth=depth)
    db.add(node)
    await db.flush()
    await db.refresh(node)
    return node


@router.patch("/{node_id}", response_model=GroupNodeRead)
async def update_group(node_id: int, body: GroupNodeUpdate, db: AsyncSession = Depends(get_db)):
    node = await db.get(GroupNode, node_id)
    if not node:
        raise HTTPException(404, "그룹 노드를 찾을 수 없습니다")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(node, k, v)
    if body.name:
        node.full_path = await _compute_full_path(db, node.parent_id, body.name)
    await db.flush()
    await db.refresh(node)
    return node


@router.delete("/{node_id}", status_code=204)
async def delete_group(node_id: int, db: AsyncSession = Depends(get_db)):
    has_assets = await db.scalar(select(exists().where(Asset.group_id == node_id)))
    if has_assets:
        raise HTTPException(409, "이 그룹에 등록된 자산이 있어 삭제할 수 없습니다")
    node = await db.get(GroupNode, node_id)
    if node:
        await db.delete(node)
