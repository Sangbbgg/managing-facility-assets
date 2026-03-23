from datetime import datetime
from sqlalchemy import String, Boolean, JSON, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class ReportTemplate(Base):
    __tablename__ = "report_templates"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    display_name: Mapped[str] = mapped_column(String(100))
    data_source: Mapped[str] = mapped_column(String(50))
    sheet_name: Mapped[str] = mapped_column(String(100))
    columns: Mapped[list] = mapped_column(JSON, default=list)   # [{header, field, width}]
    header_color: Mapped[str] = mapped_column(String(7), default="#1F4E79")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
