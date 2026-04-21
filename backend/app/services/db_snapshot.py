from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, Integer, Numeric, String, Text, delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.sqltypes import JSON
from sqlalchemy.sql.schema import Table

from app.models import Base
from app.models.db_snapshot import DatabaseSnapshot


ROLLBACK_SNAPSHOT_TYPE = "rollback"
MANUAL_SNAPSHOT_TYPE = "manual"


def get_snapshot_tables() -> list[Table]:
    return [
        table
        for table in Base.metadata.sorted_tables
        if table.name != DatabaseSnapshot.__tablename__
    ]


def _ordered_select(table: Table):
    order_columns = []
    if "depth" in table.c:
        order_columns.append(table.c.depth)
    order_columns.extend(column for column in table.primary_key.columns)
    if not order_columns:
        order_columns.extend(table.columns)
    return select(table).order_by(*order_columns)


def serialize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: serialize_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [serialize_value(item) for item in value]
    if isinstance(value, tuple):
        return [serialize_value(item) for item in value]
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, UUID):
        return str(value)
    return value


def _parse_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def coerce_value(column_type: Any, value: Any) -> Any:
    if value is None:
        return None
    if isinstance(column_type, JSON):
        return value
    if isinstance(column_type, Boolean):
        return value if isinstance(value, bool) else str(value).lower() in {"true", "1", "y", "yes"}
    if isinstance(column_type, BigInteger):
        return int(value)
    if isinstance(column_type, Integer):
        return int(value)
    if isinstance(column_type, Numeric):
        return Decimal(str(value))
    if isinstance(column_type, Float):
        return float(value)
    if isinstance(column_type, DateTime):
        return value if isinstance(value, datetime) else _parse_datetime(str(value))
    if isinstance(column_type, Date):
        return value if isinstance(value, date) else date.fromisoformat(str(value))
    if isinstance(column_type, (String, Text)):
        return str(value)
    return value


def _coerce_row(table: Table, row: dict[str, Any]) -> dict[str, Any]:
    return {
        column.name: coerce_value(column.type, row[column.name])
        for column in table.columns
        if column.name in row
    }


async def build_snapshot_payload(db: AsyncSession) -> dict[str, Any]:
    tables_json: dict[str, list[dict[str, Any]]] = {}
    table_counts_json: list[dict[str, Any]] = []

    for table in get_snapshot_tables():
        result = await db.execute(_ordered_select(table))
        rows = [
            {key: serialize_value(value) for key, value in row.items()}
            for row in result.mappings().all()
        ]
        tables_json[table.name] = rows
        table_counts_json.append({"name": table.name, "rows": len(rows)})

    table_counts_json.sort(key=lambda item: item["name"])
    row_count = sum(item["rows"] for item in table_counts_json)
    return {
        "tables_json": tables_json,
        "table_counts_json": table_counts_json,
        "table_count": len(table_counts_json),
        "row_count": row_count,
    }


async def create_snapshot(
    db: AsyncSession,
    name: str,
    description: str | None = None,
    snapshot_type: str = MANUAL_SNAPSHOT_TYPE,
    restored_from_snapshot_id: int | None = None,
) -> DatabaseSnapshot:
    payload = await build_snapshot_payload(db)
    snapshot = DatabaseSnapshot(
        name=name.strip(),
        description=(description or "").strip() or None,
        snapshot_type=snapshot_type,
        restored_from_snapshot_id=restored_from_snapshot_id,
        table_count=payload["table_count"],
        row_count=payload["row_count"],
        table_counts_json=payload["table_counts_json"],
        payload_json=payload["tables_json"],
    )
    db.add(snapshot)
    await db.flush()
    await db.refresh(snapshot)
    return snapshot


async def list_snapshots(db: AsyncSession) -> list[DatabaseSnapshot]:
    result = await db.execute(
        select(DatabaseSnapshot).order_by(DatabaseSnapshot.created_at.desc(), DatabaseSnapshot.id.desc())
    )
    return result.scalars().all()


async def get_snapshot_or_404(db: AsyncSession, snapshot_id: int) -> DatabaseSnapshot:
    snapshot = await db.get(DatabaseSnapshot, snapshot_id)
    if not snapshot:
        from fastapi import HTTPException

        raise HTTPException(404, "스냅샷을 찾을 수 없습니다")
    return snapshot


async def clear_rollback_snapshots(db: AsyncSession) -> None:
    await db.execute(
        delete(DatabaseSnapshot).where(DatabaseSnapshot.snapshot_type == ROLLBACK_SNAPSHOT_TYPE)
    )
    await db.flush()


async def apply_snapshot_payload(db: AsyncSession, payload_json: dict[str, list[dict[str, Any]]]) -> None:
    tables = get_snapshot_tables()
    joined_tables = ", ".join(f'"{table.name}"' for table in reversed(tables))
    await db.execute(text(f"TRUNCATE TABLE {joined_tables} RESTART IDENTITY CASCADE"))

    for table in tables:
        rows = payload_json.get(table.name, [])
        if not rows:
            continue
        await db.execute(table.insert(), [_coerce_row(table, row) for row in rows])


async def restore_snapshot(
    db: AsyncSession,
    snapshot: DatabaseSnapshot,
    create_rollback_snapshot: bool = True,
) -> DatabaseSnapshot | None:
    rollback_snapshot = None
    if create_rollback_snapshot:
        await clear_rollback_snapshots(db)
        rollback_snapshot = await create_snapshot(
            db,
            name=f"복원 취소 지점 - {snapshot.name}",
            description=f"'{snapshot.name}' 스냅샷 로드 직전 상태",
            snapshot_type=ROLLBACK_SNAPSHOT_TYPE,
            restored_from_snapshot_id=snapshot.id,
        )

    await apply_snapshot_payload(db, snapshot.payload_json or {})
    return rollback_snapshot


async def rollback_last_restore(db: AsyncSession) -> DatabaseSnapshot:
    result = await db.execute(
        select(DatabaseSnapshot)
        .where(DatabaseSnapshot.snapshot_type == ROLLBACK_SNAPSHOT_TYPE)
        .order_by(DatabaseSnapshot.created_at.desc(), DatabaseSnapshot.id.desc())
        .limit(1)
    )
    rollback_snapshot = result.scalar_one_or_none()
    if not rollback_snapshot:
        from fastapi import HTTPException

        raise HTTPException(404, "취소할 스냅샷 복원 이력이 없습니다")

    await apply_snapshot_payload(db, rollback_snapshot.payload_json or {})
    await db.delete(rollback_snapshot)
    await db.flush()
    return rollback_snapshot
