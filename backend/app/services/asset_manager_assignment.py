from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset
from app.models.master import PersonGroupRole


PRIMARY_ROLE = "PRIMARY"


async def resolve_group_manager_id(db: AsyncSession, group_id: int | None) -> int | None:
    if not group_id:
        return None

    result = await db.execute(
        select(PersonGroupRole.person_id)
        .where(
            PersonGroupRole.group_id == group_id,
            PersonGroupRole.role_type == PRIMARY_ROLE,
        )
        .order_by(PersonGroupRole.id)
        .limit(1)
    )
    return result.scalar_one_or_none()


async def assign_asset_manager_if_missing(db: AsyncSession, asset: Asset) -> int | None:
    if asset.manager_id is not None:
        return asset.manager_id

    asset.manager_id = await resolve_group_manager_id(db, asset.group_id)
    return asset.manager_id


async def backfill_asset_managers_for_groups(
    db: AsyncSession,
    group_ids: Iterable[int | None],
) -> int:
    normalized_group_ids = sorted({group_id for group_id in group_ids if group_id})
    if not normalized_group_ids:
        return 0

    role_rows = (
        await db.execute(
            select(PersonGroupRole)
            .where(
                PersonGroupRole.group_id.in_(normalized_group_ids),
                PersonGroupRole.role_type == PRIMARY_ROLE,
            )
            .order_by(PersonGroupRole.group_id, PersonGroupRole.id)
        )
    ).scalars().all()

    default_manager_map: dict[int, int] = {}
    for role in role_rows:
        default_manager_map.setdefault(role.group_id, role.person_id)

    if not default_manager_map:
        return 0

    assets = (
        await db.execute(
            select(Asset)
            .where(
                Asset.group_id.in_(list(default_manager_map.keys())),
                Asset.manager_id.is_(None),
                Asset.is_deleted == False,
            )
            .order_by(Asset.id)
        )
    ).scalars().all()

    updated_count = 0
    for asset in assets:
        manager_id = default_manager_map.get(asset.group_id)
        if not manager_id:
            continue
        asset.manager_id = manager_id
        updated_count += 1

    if updated_count:
        await db.flush()

    return updated_count
