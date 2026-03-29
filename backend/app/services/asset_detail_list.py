from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset
from app.models.master import EquipmentType, GroupNode, LocationNode, Person, PersonGroupRole


async def fetch_asset_detail_list(db: AsyncSession) -> list[dict]:
    assets = (
        await db.execute(
            select(Asset)
            .where(Asset.is_deleted == False)
            .order_by(Asset.asset_code)
        )
    ).scalars().all()

    groups = {row.id: row for row in (await db.execute(select(GroupNode))).scalars()}
    locations = {row.id: row for row in (await db.execute(select(LocationNode))).scalars()}
    equipment_types = {row.id: row for row in (await db.execute(select(EquipmentType))).scalars()}
    persons = {row.id: row for row in (await db.execute(select(Person))).scalars()}

    group_role_map: dict[int, int] = {}
    group_roles = (
        await db.execute(
            select(PersonGroupRole).order_by(PersonGroupRole.group_id, PersonGroupRole.id)
        )
    ).scalars().all()
    for role in group_roles:
        group_role_map.setdefault(role.group_id, role.person_id)

    rows: list[dict] = []
    for asset in assets:
        group = groups.get(asset.group_id)
        location = locations.get(asset.location_id)
        equipment_type = equipment_types.get(asset.equipment_type_id)

        resolved_manager_id = asset.manager_id or group_role_map.get(asset.group_id)
        resolved_manager = persons.get(resolved_manager_id) if resolved_manager_id else None
        explicit_manager = persons.get(asset.manager_id) if asset.manager_id else None

        rows.append(
            {
                "id": asset.id,
                "asset_code": asset.asset_code,
                "asset_name": asset.asset_name,
                "purpose": asset.purpose,
                "model_name": asset.model_name,
                "serial_number": asset.serial_number,
                "importance": asset.importance,
                "install_date": asset.install_date,
                "status": asset.status,
                "last_collected_at": asset.last_collected_at,
                "group_id": asset.group_id,
                "group_name": group.name if group else None,
                "group_full_path": group.full_path if group else None,
                "group_code": group.code if group else None,
                "group_display_code": (group.display_code or group.code) if group else None,
                "location_id": asset.location_id,
                "location_name": location.name if location else None,
                "location_full_path": location.full_path if location else None,
                "equipment_type_id": asset.equipment_type_id,
                "equipment_type_name": equipment_type.name if equipment_type else None,
                "equipment_type_code": equipment_type.code if equipment_type else None,
                "manager_id": asset.manager_id,
                "manager_name": explicit_manager.name if explicit_manager else None,
                "resolved_manager_id": resolved_manager_id,
                "resolved_manager_name": resolved_manager.name if resolved_manager else None,
            }
        )

    return rows
