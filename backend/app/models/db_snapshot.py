from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DatabaseSnapshot(Base):
    __tablename__ = "database_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    snapshot_type: Mapped[str] = mapped_column(String(20), default="manual")
    restored_from_snapshot_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("database_snapshots.id", ondelete="SET NULL"),
        nullable=True,
    )
    table_count: Mapped[int] = mapped_column(Integer, default=0)
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    table_counts_json: Mapped[list[dict]] = mapped_column(JSON, default=list)
    payload_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
