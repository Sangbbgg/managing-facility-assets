from __future__ import annotations
from datetime import date
from typing import Optional
from sqlalchemy import String, Integer, Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class LocationNode(Base):
    __tablename__ = "location_nodes"
    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("location_nodes.id", ondelete="CASCADE"), nullable=True)
    name: Mapped[str] = mapped_column(String(100))
    full_path: Mapped[str] = mapped_column(String(500))
    depth: Mapped[int] = mapped_column(Integer, default=0)
    parent: Mapped[Optional[LocationNode]] = relationship("LocationNode", remote_side="LocationNode.id", back_populates="children")
    children: Mapped[list[LocationNode]] = relationship("LocationNode", back_populates="parent")


class GroupNode(Base):
    __tablename__ = "group_nodes"
    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("group_nodes.id", ondelete="CASCADE"), nullable=True)
    name: Mapped[str] = mapped_column(String(100))
    code: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)
    full_path: Mapped[str] = mapped_column(String(500))
    depth: Mapped[int] = mapped_column(Integer, default=0)
    parent: Mapped[Optional[GroupNode]] = relationship("GroupNode", remote_side="GroupNode.id", back_populates="children")
    children: Mapped[list[GroupNode]] = relationship("GroupNode", back_populates="parent", cascade="all, delete-orphan", passive_deletes=True)


class EquipmentType(Base):
    __tablename__ = "equipment_types"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    code: Mapped[str] = mapped_column(String(10), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class OsCatalog(Base):
    __tablename__ = "os_catalog"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    eol_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    extended_eol: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class AntivirusCatalog(Base):
    __tablename__ = "antivirus_catalog"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    support_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Department(Base):
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)


class Person(Base):
    __tablename__ = "persons"
    id: Mapped[int] = mapped_column(primary_key=True)
    dept_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(50))
    title: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    contact: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
