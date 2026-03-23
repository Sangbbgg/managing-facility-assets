from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.asset import AssetCodeSequence
from app.core.config import settings


async def issue_asset_code(db: AsyncSession, group_code: str, type_code: str) -> str:
    stmt = (
        select(AssetCodeSequence)
        .where(
            AssetCodeSequence.group_code == group_code,
            AssetCodeSequence.type_code == type_code,
        )
        .with_for_update()
    )
    seq_row = await db.scalar(stmt)
    if seq_row is None:
        seq_row = AssetCodeSequence(group_code=group_code, type_code=type_code, last_seq=0)
        db.add(seq_row)
        await db.flush()
    seq_row.last_seq += 1
    return f"{settings.ASSET_PREFIX}-{group_code}-{type_code}-{seq_row.last_seq:04d}"
