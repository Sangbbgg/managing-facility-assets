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
    equipment_type_links = relationship(
        "ReportFormTemplateEquipmentType",
        back_populates="template",
        cascade="all, delete-orphan",
    )
    group_links = relationship(
        "ReportFormTemplateGroup",
        back_populates="template",
        cascade="all, delete-orphan",
    )


class ReportFormTemplateEquipmentType(Base):
    __tablename__ = "report_form_template_equipment_types"

    template_id = Column(
        Integer,
        ForeignKey("report_form_templates.id", ondelete="CASCADE"),
        primary_key=True,
    )
    equipment_type_id = Column(
        Integer,
        ForeignKey("equipment_types.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    template = relationship("ReportFormTemplate", back_populates="equipment_type_links")
    equipment_type = relationship("EquipmentType")


class ReportFormTemplateGroup(Base):
    __tablename__ = "report_form_template_groups"

    template_id = Column(
        Integer,
        ForeignKey("report_form_templates.id", ondelete="CASCADE"),
        primary_key=True,
    )
    group_id = Column(
        Integer,
        ForeignKey("group_nodes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    template = relationship("ReportFormTemplate", back_populates="group_links")
    group = relationship("GroupNode")


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
    named_range_name = Column(String(120), nullable=True)
    page_range_name = Column(String(120), nullable=True)
    overflow_mode = Column(String(30), nullable=True)
    block_start_row = Column(Integer, nullable=True)
    block_end_row = Column(Integer, nullable=True)
    block_start_col = Column(String(10), nullable=True)
    block_end_col = Column(String(10), nullable=True)
    page_subblock_count = Column(Integer, nullable=True)
    page_subblock_width = Column(Integer, nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    template = relationship("ReportFormTemplate", back_populates="mappings")
