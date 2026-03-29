from __future__ import annotations
from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Integer, BigInteger, Boolean, Date, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class AssetHwSystem(Base):
    __tablename__ = "asset_hw_systems"
    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    manufacturer: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    system_model: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    system_serial: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    system_uuid: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    os_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    os_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    os_build: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    os_arch: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    system_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    bios_version: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    total_memory_mb: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    hostname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    domain: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    install_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    last_boot: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    raw_csproduct: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    raw_os: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    raw_systeminfo: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class AssetHwCpu(Base):
    __tablename__ = "asset_hw_cpus"
    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    manufacturer: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    cores: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    logical_cpus: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_clock_mhz: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    architecture: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    socket: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    raw_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class AssetHwMemory(Base):
    __tablename__ = "asset_hw_memories"
    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    locator: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    capacity_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    speed_mhz: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    manufacturer: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    part_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    serial_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    form_factor: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    raw_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class AssetHwDisk(Base):
    __tablename__ = "asset_hw_disks"
    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    model: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    interface_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    serial_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    media_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    partitions: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    raw_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class AssetHwGpu(Base):
    __tablename__ = "asset_hw_gpus"
    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    driver_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    video_memory_mb: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    resolution: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    raw_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class AssetHwNic(Base):
    __tablename__ = "asset_hw_nics"
    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    adapter_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    connection_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    mac_address: Mapped[Optional[str]] = mapped_column(String(17), nullable=True)
    ipv4_address: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    subnet_mask: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    default_gateway: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    dns_servers: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    dhcp_enabled: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    is_unused: Mapped[bool] = mapped_column(Boolean, default=False)
    raw_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
