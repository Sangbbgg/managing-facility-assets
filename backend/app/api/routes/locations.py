from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, text
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


async def _get_descendant_ids(db: AsyncSession, node_id: int) -> list[int]:
    result = await db.execute(text("""
        WITH RECURSIVE descendants AS (
            SELECT id FROM location_nodes WHERE id = :node_id
            UNION ALL
            SELECT l.id FROM location_nodes l
            INNER JOIN descendants d ON l.parent_id = d.id
        )
        SELECT id FROM descendants
    """), {"node_id": node_id})
    return [row[0] for row in result.fetchall()]


async def _validate_parent(db: AsyncSession, node_id: int, parent_id: int | None) -> None:
    if parent_id is None:
        return
    if parent_id == node_id:
        raise HTTPException(400, "자기 자신을 상위 노드로 지정할 수 없습니다")
    descendant_ids = await _get_descendant_ids(db, node_id)
    if parent_id in descendant_ids:
        raise HTTPException(400, "하위 노드 아래로 이동할 수 없습니다")


async def _refresh_subtree_paths(db: AsyncSession, root_id: int) -> None:
    result = await db.execute(select(LocationNode).order_by(LocationNode.depth, LocationNode.id))
    nodes = result.scalars().all()
    by_id = {node.id: node for node in nodes}
    by_parent: dict[int | None, list[LocationNode]] = {}
    for node in nodes:
        by_parent.setdefault(node.parent_id, []).append(node)

    root = by_id.get(root_id)
    if not root:
        return

    def _apply(parent: LocationNode) -> None:
        for child in by_parent.get(parent.id, []):
            child.full_path = f"{parent.full_path} > {child.name}"
            child.depth = parent.depth + 1
            _apply(child)

    _apply(root)


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
    data = body.model_dump(exclude_unset=True)
    if "parent_id" in data:
        await _validate_parent(db, node_id, data["parent_id"])
    for k, v in data.items():
        setattr(node, k, v)
    if "name" in data or "parent_id" in data:
        node.full_path = await _compute_full_path(db, node.parent_id, node.name)
        node.depth = await _compute_depth(db, node.parent_id)
        await _refresh_subtree_paths(db, node.id)
    await db.flush()
    await db.refresh(node)
    return node


@router.delete("/{node_id}", status_code=204)
async def delete_location(node_id: int, db: AsyncSession = Depends(get_db)):
    ids = await _get_descendant_ids(db, node_id)
    has_assets = await db.scalar(select(exists().where(Asset.location_id.in_(ids))))
    if has_assets:
        raise HTTPException(409, "이 위치 또는 하위 위치에 등록된 자산이 있어 삭제할 수 없습니다")
    node = await db.get(LocationNode, node_id)
    if node:
        await db.delete(node)
