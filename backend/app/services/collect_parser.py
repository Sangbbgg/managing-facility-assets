import csv
import io
import json
import zipfile
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.hw_info import (
    AssetHwSystem, AssetHwCpu, AssetHwMemory,
    AssetHwDisk, AssetHwGpu, AssetHwNic,
)
from app.models.sw_info import AssetSwProduct, AssetSwHotfix, AssetSwProcess
from app.models.asset import Asset


async def parse_powershell_json(data: dict, asset_id: int, db: AsyncSession) -> dict:
    collected_at = _parse_datetime(data.get("_meta", {}).get("collected_at"))
    summary = {}

    if "system" in data:
        sys_data = data["system"] or {}
        cs = sys_data.get("csproduct") or {}
        os_info = sys_data.get("os") or {}
        ci = sys_data.get("computerinfo") or {}
        if isinstance(cs, list): cs = cs[0] if cs else {}
        if isinstance(os_info, list): os_info = os_info[0] if os_info else {}
        db.add(AssetHwSystem(
            asset_id=asset_id, collected_at=collected_at,
            manufacturer=cs.get("Vendor") or ci.get("CsManufacturer"),
            system_model=cs.get("Name") or ci.get("CsModel"),
            system_serial=cs.get("IdentifyingNumber"),
            system_uuid=cs.get("UUID"),
            os_name=os_info.get("Caption") or ci.get("OsName"),
            os_version=os_info.get("Version") or ci.get("OsVersion"),
            os_build=os_info.get("BuildNumber") or ci.get("OsBuildNumber"),
            os_arch=os_info.get("OSArchitecture") or ci.get("OsArchitecture"),
            system_type=ci.get("CsSystemType"),
            bios_version=ci.get("BiosSMBIOSBIOSVersion"),
            total_memory_mb=_bytes_to_mb(os_info.get("TotalVisibleMemorySize")),
            hostname=data.get("_meta", {}).get("hostname"),
            raw_csproduct=cs, raw_os=os_info, raw_systeminfo=ci,
        ))
        summary["system"] = 1

    if "cpu" in data:
        items = _ensure_list(data["cpu"])
        for item in items:
            db.add(AssetHwCpu(
                asset_id=asset_id, collected_at=collected_at,
                name=item.get("Name"), manufacturer=item.get("Manufacturer"),
                cores=item.get("NumberOfCores"), logical_cpus=item.get("NumberOfLogicalProcessors"),
                max_clock_mhz=item.get("MaxClockSpeed"),
                architecture=_arch_name(item.get("Architecture")),
                socket=item.get("SocketDesignation"), raw_json=item,
            ))
        summary["cpu"] = len(items)

    if "memory" in data:
        items = _ensure_list(data["memory"])
        for item in items:
            db.add(AssetHwMemory(
                asset_id=asset_id, collected_at=collected_at,
                locator=item.get("DeviceLocator"), capacity_bytes=item.get("Capacity"),
                speed_mhz=item.get("Speed"), manufacturer=item.get("Manufacturer"),
                serial_number=_clean(item.get("SerialNumber")),
                form_factor=str(item.get("FormFactor", "")), raw_json=item,
            ))
        summary["memory"] = len(items)

    if "disk" in data:
        items = _ensure_list(data["disk"])
        for item in items:
            db.add(AssetHwDisk(
                asset_id=asset_id, collected_at=collected_at,
                model=item.get("Model"), size_bytes=item.get("Size"),
                interface_type=item.get("InterfaceType"),
                serial_number=_clean(item.get("SerialNumber")),
                media_type=item.get("MediaType"), partitions=item.get("Partitions"),
                raw_json=item,
            ))
        summary["disk"] = len(items)

    if "gpu" in data:
        items = _ensure_list(data["gpu"])
        for item in items:
            db.add(AssetHwGpu(
                asset_id=asset_id, collected_at=collected_at,
                name=item.get("Name"), driver_version=item.get("DriverVersion"),
                video_memory_mb=_bytes_to_mb(item.get("AdapterRAM")),
                resolution=item.get("VideoModeDescription"), raw_json=item,
            ))
        summary["gpu"] = len(items)

    if "nic" in data:
        items = _ensure_list(data["nic"])
        for item in items:
            db.add(AssetHwNic(
                asset_id=asset_id, collected_at=collected_at,
                adapter_name=item.get("InterfaceDescription"),
                connection_name=item.get("InterfaceAlias"),
                mac_address=item.get("MacAddress"),
                ipv4_address=_extract_ip(item.get("IPv4Address")),
                dhcp_enabled=item.get("DHCPEnabled"), raw_json=item,
            ))
        summary["nic"] = len(items)

    if "product" in data:
        items = [i for i in _ensure_list(data["product"]) if i.get("Name")]
        for item in items:
            db.add(AssetSwProduct(
                asset_id=asset_id, collected_at=collected_at,
                name=item.get("Name"), version=item.get("Version"),
                vendor=item.get("Vendor"),
                install_date=_parse_date(item.get("InstallDate")),
                raw_json=item,
            ))
        summary["product"] = len(items)

    if "hotfix" in data:
        items = _ensure_list(data["hotfix"])
        for item in items:
            db.add(AssetSwHotfix(
                asset_id=asset_id, collected_at=collected_at,
                hotfix_id=item.get("HotFixID"), description=item.get("Description"),
                installed_on=_parse_date(item.get("InstalledOn")),
                installed_by=item.get("InstalledBy"), raw_json=item,
            ))
        summary["hotfix"] = len(items)

    if "process" in data:
        items = _ensure_list(data["process"])
        for item in items:
            db.add(AssetSwProcess(
                asset_id=asset_id, collected_at=collected_at,
                process_name=item.get("ProcessName"),
                pid=item.get("Id"), session_name=str(item.get("SessionId", "")),
                memory_kb=item.get("WorkingSetKB") or item.get("WorkingSet64"),
                raw_json=item,
            ))
        summary["process"] = len(items)

    # assets.last_collected_at 갱신
    asset = await db.get(Asset, asset_id)
    if asset:
        asset.last_collected_at = collected_at

    await db.flush()
    return summary


async def parse_legacy_zip(zip_bytes: bytes, asset_id: int, db: AsyncSession) -> dict:
    FILE_MAP = {
        "csproduct.txt": ("system", "csproduct"),
        "os.txt": ("system", "os"),
        "systeminfo.txt": ("system", "computerinfo"),
        "cpu.txt": ("cpu", None),
        "memorychip.txt": ("memory", None),
        "diskdrive.txt": ("disk", None),
        "videocontroller.txt": ("gpu", None),
        "hotfix.txt": ("hotfix", None),
        "product.txt": ("product", None),
        "process.txt": ("process", None),
    }

    result_data: dict = {"_meta": {"collected_at": datetime.now(), "hostname": "legacy"}}

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for zpath in zf.namelist():
            fname = zpath.split('/')[-1].lower()
            if fname not in FILE_MAP:
                continue
            target_key, sub_key = FILE_MAP[fname]
            try:
                content = zf.read(zpath).decode("euc-kr", errors="replace")
                rows = list(csv.DictReader(io.StringIO(content)))
                if sub_key:
                    result_data.setdefault("system", {})[sub_key] = rows[0] if rows else {}
                else:
                    result_data[target_key] = rows
            except Exception:
                continue

    return await parse_powershell_json(result_data, asset_id, db)


# === 유틸리티 ===
def _ensure_list(val) -> list:
    if val is None: return []
    if isinstance(val, list): return val
    return [val]

def _clean(val: Optional[str]) -> Optional[str]:
    if val is None: return None
    return val.strip() or None

def _bytes_to_mb(val) -> Optional[int]:
    if val is None: return None
    try:
        v = int(val)
        return v // (1024 * 1024) if v > 1_000_000 else v // 1024
    except (ValueError, TypeError):
        return None

def _arch_name(val) -> Optional[str]:
    arch_map = {0: "x86", 9: "x64", 5: "ARM", 12: "ARM64"}
    try: return arch_map.get(int(val), str(val))
    except: return str(val) if val else None

def _parse_date(val):
    if val is None: return None
    from datetime import date
    try:
        s = str(val).replace("/", "-").strip()
        if len(s) == 8 and s.isdigit():
            return date(int(s[:4]), int(s[4:6]), int(s[6:8]))
        return date.fromisoformat(s[:10])
    except: return None

def _extract_ip(val) -> Optional[str]:
    if val is None: return None
    if isinstance(val, list): val = val[0] if val else None
    if isinstance(val, dict): val = val.get("IPAddress")
    return str(val).strip() if val else None

def _parse_datetime(val) -> datetime:
    """ISO 문자열 또는 datetime 객체를 datetime으로 변환. asyncpg는 str 거부."""
    if val is None:
        return datetime.now()
    if isinstance(val, datetime):
        return val
    try:
        # Python 3.11+ fromisoformat handles timezone offsets like +09:00
        return datetime.fromisoformat(str(val))
    except (ValueError, TypeError):
        return datetime.now()
