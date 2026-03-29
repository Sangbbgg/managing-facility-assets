from __future__ import annotations
from datetime import date, datetime
from typing import Optional
from sqlalchemy import Boolean, String, Integer, Date, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class AssetSwProduct(Base):
    __tablename__ = "asset_sw_products"
    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    name: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    version: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    vendor: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    install_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    raw_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class AssetSwHotfix(Base):
    __tablename__ = "asset_sw_hotfixes"
    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    hotfix_id: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    installed_on: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    installed_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    raw_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class AssetSwProcess(Base):
    __tablename__ = "asset_sw_processes"
    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    process_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    pid: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    session_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    memory_kb: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    raw_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class AssetSwAccount(Base):
    __tablename__ = "asset_sw_accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    account_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    enabled: Mapped[Optional[bool]] = mapped_column(nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    raw_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
