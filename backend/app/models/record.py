from __future__ import annotations
from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class InspectionRecord(Base):
    __tablename__ = "inspection_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    record_date: Mapped[date] = mapped_column(Date, index=True)
    inspection_type: Mapped[str] = mapped_column(String(20))  # MONTHLY / QUARTERLY
    check_items: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    result: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    special_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    inspector: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class EventLogRecord(Base):
    __tablename__ = "event_log_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    record_date: Mapped[date] = mapped_column(Date, index=True)
    log_type: Mapped[str] = mapped_column(String(10))    # app / sec / sys
    event_id: Mapped[int] = mapped_column(Integer)
    level: Mapped[int] = mapped_column(Integer)          # 1=Critical 2=Error 3=Warning
    count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class ConsoleAccessRecord(Base):
    __tablename__ = "console_access_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    access_date: Mapped[date] = mapped_column(Date, index=True)
    accessor: Mapped[str] = mapped_column(String(50))
    purpose: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class SealRecord(Base):
    __tablename__ = "seal_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    record_date: Mapped[date] = mapped_column(Date, index=True)
    seal_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    action: Mapped[str] = mapped_column(String(20))      # ATTACH / REMOVE / CHECK
    handler: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class PasswordRecord(Base):
    __tablename__ = "password_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    account_name: Mapped[str] = mapped_column(String(100))
    changed_date: Mapped[date] = mapped_column(Date, index=True)
    changed_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
