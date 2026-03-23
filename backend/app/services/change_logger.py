from sqlalchemy.ext.asyncio import AsyncSession
from app.models.asset import AssetChangeLog


async def log_changes(
    db: AsyncSession,
    asset_id: int,
    changed_by: str,
    old_data: dict,
    new_data: dict,
    reason: str = "",
):
    """old_data와 new_data를 비교하여 변경된 필드만 이력 기록"""
    for field, new_val in new_data.items():
        old_val = old_data.get(field)
        if str(old_val) != str(new_val):
            db.add(AssetChangeLog(
                asset_id=asset_id,
                changed_by=changed_by,
                field_name=field,
                old_value=str(old_val) if old_val is not None else None,
                new_value=str(new_val) if new_val is not None else None,
                reason=reason,
            ))
    await db.flush()
