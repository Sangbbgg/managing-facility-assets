from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ReportFormTemplateFolder(Base):
    __tablename__ = "report_form_template_folders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    templates = relationship("ReportFormTemplate", back_populates="folder")


class ReportFormTemplate(Base):
    __tablename__ = "report_form_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    file_name = Column(String(300), nullable=False)
    file_path = Column(String(500), nullable=False)
    category = Column(String(50), default="general")
    folder_id = Column(Integer, ForeignKey("report_form_template_folders.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    folder = relationship("ReportFormTemplateFolder", back_populates="templates")
    mappings = relationship("ReportFormMapping", back_populates="template", cascade="all, delete-orphan")


class ReportFormMapping(Base):
    __tablename__ = "report_form_mappings"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("report_form_templates.id", ondelete="CASCADE"), nullable=False)
    sheet_name = Column(String(100), nullable=True)
    cell = Column(String(10), nullable=False)
    data_source = Column(String(30), nullable=False)
    field = Column(String(100), nullable=False)
    secondary_field = Column(String(100), nullable=True)
    display_label = Column(String(100), nullable=True)
    format = Column(String(100), nullable=True)
    aggregate_mode = Column(String(30), nullable=True)
    output_template = Column(String(300), nullable=True)
    repeat_direction = Column(String(10), nullable=True)
    repeat_max_rows = Column(Integer, nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    template = relationship("ReportFormTemplate", back_populates="mappings")
