from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    asset_name: Mapped[str] = mapped_column(String(100))
    purpose: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    importance: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    install_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    representative_nic_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    representative_account_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="OPERATING")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    last_collected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    group_id: Mapped[Optional[int]] = mapped_column(ForeignKey("group_nodes.id"), nullable=True)
    location_id: Mapped[Optional[int]] = mapped_column(ForeignKey("location_nodes.id"), nullable=True)
    equipment_type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("equipment_types.id"), nullable=True)
    manager_id: Mapped[Optional[int]] = mapped_column(ForeignKey("persons.id"), nullable=True)
    custom_fields_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    manager: Mapped[Optional["Person"]] = relationship("Person", foreign_keys=[manager_id])


class AssetCodeSequence(Base):
    __tablename__ = "asset_code_sequences"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_code: Mapped[str] = mapped_column(String(20))
    type_code: Mapped[str] = mapped_column(String(10))
    last_seq: Mapped[int] = mapped_column(Integer, default=0)


class AssetChangeLog(Base):
    __tablename__ = "asset_change_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    changed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    changed_by: Mapped[str] = mapped_column(String(50))
    field_name: Mapped[str] = mapped_column(String(50))
    old_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
