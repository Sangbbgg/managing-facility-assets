from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.asset import AssetCodeSequence
from app.core.config import settings


async def get_next_asset_code_parts(
    db: AsyncSession,
    sequence_group_code: str,
    display_group_code: str,
    type_code: str,
    *,
    increment: bool,
) -> tuple[str, int]:
    stmt = (
        select(AssetCodeSequence)
        .where(
            AssetCodeSequence.group_code == sequence_group_code,
            AssetCodeSequence.type_code == type_code,
        )
        .with_for_update()
    )
    seq_row = await db.scalar(stmt)
    if seq_row is None:
        seq_row = AssetCodeSequence(group_code=sequence_group_code, type_code=type_code, last_seq=0)
        db.add(seq_row)
        await db.flush()

    next_seq = seq_row.last_seq + 1
    asset_code = f"{settings.ASSET_PREFIX}-{display_group_code}-{type_code}-{next_seq:04d}"

    if increment:
        seq_row.last_seq = next_seq

    return asset_code, next_seq


async def preview_asset_code(
    db: AsyncSession,
    sequence_group_code: str,
    display_group_code: str,
    type_code: str,
) -> tuple[str, int]:
    return await get_next_asset_code_parts(
        db,
        sequence_group_code,
        display_group_code,
        type_code,
        increment=False,
    )


async def issue_asset_code(
    db: AsyncSession,
    sequence_group_code: str,
    display_group_code: str,
    type_code: str,
) -> str:
    asset_code, _ = await get_next_asset_code_parts(
        db,
        sequence_group_code,
        display_group_code,
        type_code,
        increment=True,
    )
    return asset_code
