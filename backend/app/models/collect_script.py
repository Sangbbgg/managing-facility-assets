from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Boolean, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class CollectScript(Base):
    __tablename__ = "collect_scripts"
    id: Mapped[int] = mapped_column(primary_key=True)
    script_key: Mapped[str] = mapped_column(String(50), unique=True)
    display_name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    legacy_command: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    ps_command: Mapped[str] = mapped_column(Text)
    ps_filename: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    target_table: Mapped[str] = mapped_column(String(100))
    output_format: Mapped[str] = mapped_column(String(20), default="json")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
