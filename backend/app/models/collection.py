from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AssetCollectRun(Base):
    __tablename__ = "asset_collect_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)
    source_type: Mapped[str] = mapped_column(String(30), default="powershell")
    collector_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    hostname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    status: Mapped[str] = mapped_column(String(20), default="SUCCESS")
    raw_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AssetNetworkConnection(Base):
    __tablename__ = "asset_network_connections"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    protocol: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    local_address: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    remote_address: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    process_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    raw_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
