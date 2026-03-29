import csv
import io
import json
import zipfile
from datetime import date, datetime
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset
from app.models.collection import AssetCollectRun, AssetNetworkConnection
from app.models.hw_info import (
    AssetHwCpu,
    AssetHwDisk,
    AssetHwGpu,
    AssetHwMemory,
    AssetHwNic,
    AssetHwSystem,
)
from app.models.sw_info import AssetSwAccount, AssetSwHotfix, AssetSwProcess, AssetSwProduct


HW_SW_MODELS = [
    AssetHwSystem,
    AssetHwCpu,
    AssetHwMemory,
    AssetHwDisk,
    AssetHwGpu,
    AssetHwNic,
    AssetSwProduct,
    AssetSwHotfix,
    AssetSwProcess,
    AssetSwAccount,
    AssetNetworkConnection,
]


async def parse_powershell_json(data: dict, asset_id: int, db: AsyncSession) -> dict:
    normalized = _normalize_collect_payload(data)
    meta = normalized["meta"]
    summary_data = normalized["summary"]
    network_data = normalized["network"]
    software_items = normalized["software"]
    process_items = normalized["processes"]
    account_items = normalized["accounts"]
    hotfix_items = normalized["hotfixes"]
    collected_at = _parse_datetime(meta.get("collected_at"))
    previous_rep_nic = await _get_representative_nic_signature(asset_id, db)
    previous_unused_nics = await _get_unused_nic_signatures(asset_id, db)
    previous_rep_account = await _get_representative_account_signature(asset_id, db)

    await _clear_existing_collect_rows(db, asset_id)

    db.add(
        AssetCollectRun(
            asset_id=asset_id,
            source_type=meta.get("source") or "powershell",
            collector_version=meta.get("collector_version"),
            hostname=meta.get("hostname"),
            collected_at=collected_at,
            status="SUCCESS",
            raw_payload=normalized,
        )
    )

    summary: dict[str, int] = {}
    nic_entities: list[AssetHwNic] = []

    if summary_data:
        db.add(
            AssetHwSystem(
                asset_id=asset_id,
                collected_at=collected_at,
                manufacturer=summary_data.get("manufacturer"),
                system_model=summary_data.get("model_name"),
                system_serial=summary_data.get("serial_number"),
                system_uuid=summary_data.get("system_uuid"),
                os_name=summary_data.get("os_name"),
                os_version=summary_data.get("os_version"),
                os_build=summary_data.get("os_build"),
                os_arch=summary_data.get("os_architecture"),
                system_type=summary_data.get("system_type"),
                bios_version=summary_data.get("bios_version"),
                total_memory_mb=_memory_to_mb(summary_data.get("memory_total")),
                hostname=summary_data.get("hostname") or meta.get("hostname"),
                domain=summary_data.get("domain"),
                install_date=_parse_date(summary_data.get("install_date")),
                last_boot=_parse_datetime(summary_data.get("last_boot")) if summary_data.get("last_boot") else None,
                raw_csproduct=summary_data.get("raw_csproduct"),
                raw_os=summary_data.get("raw_os"),
                raw_systeminfo=summary_data,
            )
        )
        summary["system"] = 1

    for item in _ensure_list(summary_data.get("cpu_items")):
        db.add(
            AssetHwCpu(
                asset_id=asset_id,
                collected_at=collected_at,
                name=item.get("name") or item.get("Name") or summary_data.get("cpu_model"),
                manufacturer=item.get("manufacturer") or item.get("Manufacturer"),
                cores=item.get("cores") or item.get("NumberOfCores"),
                logical_cpus=item.get("logical_cpus") or item.get("NumberOfLogicalProcessors"),
                max_clock_mhz=item.get("max_clock_mhz") or item.get("MaxClockSpeed"),
                architecture=_arch_name(item.get("architecture") or item.get("Architecture")),
                socket=item.get("socket") or item.get("SocketDesignation"),
                raw_json=item,
            )
        )
    if summary_data.get("cpu_model") and not summary_data.get("cpu_items"):
        db.add(
            AssetHwCpu(
                asset_id=asset_id,
                collected_at=collected_at,
                name=summary_data.get("cpu_model"),
                raw_json={"name": summary_data.get("cpu_model")},
            )
        )
        summary["cpu"] = 1
    elif summary_data.get("cpu_items"):
        summary["cpu"] = len(_ensure_list(summary_data.get("cpu_items")))

    memory_slots = _ensure_list(summary_data.get("memory_slots"))
    for item in memory_slots:
        db.add(
            AssetHwMemory(
                asset_id=asset_id,
                collected_at=collected_at,
                locator=item.get("locator") or item.get("DeviceLocator"),
                capacity_bytes=_parse_capacity_bytes(item.get("capacity") or item.get("Capacity")),
                speed_mhz=item.get("speed_mhz") or item.get("Speed"),
                manufacturer=item.get("manufacturer") or item.get("Manufacturer"),
                part_number=_clean(item.get("part_number") or item.get("PartNumber")),
                serial_number=_clean(item.get("serial_number") or item.get("SerialNumber")),
                form_factor=str(item.get("form_factor") or item.get("FormFactor") or ""),
                raw_json=item,
            )
        )
    if memory_slots:
        summary["memory"] = len(memory_slots)

    for item in _ensure_list(summary_data.get("disk_items")):
        db.add(
            AssetHwDisk(
                asset_id=asset_id,
                collected_at=collected_at,
                model=item.get("model") or item.get("Model"),
                size_bytes=item.get("size_bytes") or item.get("Size"),
                interface_type=item.get("interface_type") or item.get("InterfaceType"),
                serial_number=_clean(item.get("serial_number") or item.get("SerialNumber")),
                media_type=item.get("media_type") or item.get("MediaType"),
                partitions=item.get("partitions") or item.get("Partitions"),
                raw_json=item,
            )
        )
    for name in _ensure_list(summary_data.get("storage_devices")):
        db.add(
            AssetHwDisk(
                asset_id=asset_id,
                collected_at=collected_at,
                model=str(name),
                raw_json={"label": name},
            )
        )
    if summary_data.get("disk_items") or summary_data.get("storage_devices"):
        summary["disk"] = len(_ensure_list(summary_data.get("disk_items"))) + len(_ensure_list(summary_data.get("storage_devices")))

    gpu_items = _dedupe_gpu_items(_ensure_list(summary_data.get("gpu_items")))
    for item in gpu_items:
        db.add(
            AssetHwGpu(
                asset_id=asset_id,
                collected_at=collected_at,
                name=item.get("name") or item.get("Name"),
                driver_version=item.get("driver_version") or item.get("DriverVersion"),
                video_memory_mb=_bytes_to_mb(item.get("video_memory_bytes") or item.get("AdapterRAM")),
                resolution=item.get("resolution") or item.get("VideoModeDescription"),
                raw_json=item,
            )
        )
    if gpu_items:
        summary["gpu"] = len(gpu_items)

    nic_items = _build_nic_rows(network_data)
    for item in nic_items:
        nic = AssetHwNic(
            asset_id=asset_id,
            collected_at=collected_at,
            adapter_name=item.get("adapter_name"),
            connection_name=item.get("connection_name"),
            mac_address=item.get("mac_address"),
            ipv4_address=item.get("ipv4_address"),
            subnet_mask=item.get("subnet_mask"),
            default_gateway=item.get("default_gateway"),
            dns_servers=item.get("dns_servers"),
            dhcp_enabled=item.get("dhcp_enabled"),
            raw_json=item.get("raw_json"),
        )
        db.add(nic)
        nic_entities.append(nic)
    if nic_items:
        summary["nic"] = len(nic_items)

    for item in _ensure_list(network_data.get("connections")):
        db.add(
            AssetNetworkConnection(
                asset_id=asset_id,
                collected_at=collected_at,
                protocol=item.get("protocol"),
                local_address=item.get("local_address"),
                remote_address=item.get("remote_address"),
                state=item.get("state"),
                process_name=item.get("process_name"),
                raw_json=item,
            )
        )
    if network_data.get("connections"):
        summary["connections"] = len(_ensure_list(network_data.get("connections")))

    for item in software_items:
        db.add(
            AssetSwProduct(
                asset_id=asset_id,
                collected_at=collected_at,
                name=item.get("name") or item.get("Name"),
                version=item.get("version") or item.get("Version"),
                vendor=item.get("vendor") or item.get("Vendor"),
                install_date=_parse_date(item.get("installed_on") or item.get("install_date") or item.get("InstallDate")),
                raw_json=item,
            )
        )
    if software_items:
        summary["product"] = len(software_items)

    for item in hotfix_items:
        db.add(
            AssetSwHotfix(
                asset_id=asset_id,
                collected_at=collected_at,
                hotfix_id=item.get("hotfix_id") or item.get("HotFixID"),
                description=item.get("description") or item.get("Description"),
                installed_on=_parse_date(item.get("installed_on") or item.get("InstalledOn")),
                installed_by=item.get("installed_by") or item.get("InstalledBy"),
                raw_json=item,
            )
        )
    if hotfix_items:
        summary["hotfix"] = len(hotfix_items)

    for item in process_items:
        db.add(
            AssetSwProcess(
                asset_id=asset_id,
                collected_at=collected_at,
                process_name=item.get("name") or item.get("process_name") or item.get("ProcessName"),
                pid=item.get("pid") or item.get("Id"),
                session_name=str(item.get("session_name") or item.get("SessionId") or ""),
                memory_kb=item.get("memory_kb") or item.get("WorkingSetKB") or item.get("WorkingSet64"),
                raw_json=item,
            )
        )
    if process_items:
        summary["process"] = len(process_items)

    account_entities: list[AssetSwAccount] = []
    for item in account_items:
        account = AssetSwAccount(
            asset_id=asset_id,
            collected_at=collected_at,
            account_name=item.get("account_name") or item.get("name") or item.get("Name"),
            enabled=_to_bool(item.get("enabled") if "enabled" in item else item.get("Enabled")),
            comment=item.get("comment") or item.get("description") or item.get("Description"),
            raw_json=item,
        )
        db.add(account)
        account_entities.append(account)
    if account_items:
        summary["account"] = len(account_items)

    await db.flush()
    await _apply_asset_summary(
        asset_id,
        normalized,
        nic_entities,
        account_entities,
        previous_rep_nic,
        previous_unused_nics,
        previous_rep_account,
        db,
    )
    await db.flush()
    return summary


async def parse_legacy_zip(zip_bytes: bytes, asset_id: int, db: AsyncSession) -> dict:
    file_map = {
        "csproduct.txt": ("system", "csproduct"),
        "os.txt": ("system", "os"),
        "systeminfo.txt": ("system", "computerinfo"),
        "cpu.txt": ("cpu", None),
        "memorychip.txt": ("memory", None),
        "diskdrive.txt": ("disk", None),
        "videocontroller.txt": ("gpu", None),
        "nic.txt": ("nic", None),
        "hotfix.txt": ("hotfix", None),
        "product.txt": ("product", None),
        "process.txt": ("process", None),
        "connections.txt": ("connections", None),
        "netstat.txt": ("connections", None),
    }

    result_data: dict = {"_meta": {"collected_at": datetime.now(), "hostname": "legacy"}}

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for zpath in zf.namelist():
            fname = zpath.split("/")[-1].lower()
            if fname not in file_map:
                continue
            target_key, sub_key = file_map[fname]
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


async def _clear_existing_collect_rows(db: AsyncSession, asset_id: int) -> None:
    for model in HW_SW_MODELS:
        await db.execute(delete(model).where(model.asset_id == asset_id))


async def _apply_asset_summary(
    asset_id: int,
    normalized: dict,
    nic_entities: list[AssetHwNic],
    account_entities: list[AssetSwAccount],
    previous_rep_nic: Optional[dict],
    previous_unused_nics: list[dict],
    previous_rep_account: Optional[dict],
    db: AsyncSession,
) -> None:
    asset = await db.get(Asset, asset_id)
    if not asset:
        return

    meta = normalized.get("meta", {})
    summary_data = normalized.get("summary", {})
    network_data = normalized.get("network", {})
    collected_at = _parse_datetime(meta.get("collected_at"))

    asset.last_collected_at = collected_at

    hostname = summary_data.get("hostname") or meta.get("hostname")
    if hostname and not asset.asset_name:
        asset.asset_name = hostname

    _remap_representative_nic(asset, nic_entities, previous_rep_nic)
    _remap_unused_nics(asset, nic_entities, previous_unused_nics)
    _remap_representative_account(asset, account_entities, previous_rep_account)


async def _get_representative_nic_signature(asset_id: int, db: AsyncSession) -> Optional[dict]:
    asset = await db.get(Asset, asset_id)
    if not asset or not asset.representative_nic_id:
        return None

    nic = await db.get(AssetHwNic, asset.representative_nic_id)
    if not nic or nic.asset_id != asset_id:
        return None

    return {
        "adapter_name": nic.adapter_name,
        "connection_name": nic.connection_name,
        "mac_address": nic.mac_address,
        "ipv4_address": nic.ipv4_address,
    }


async def _get_unused_nic_signatures(asset_id: int, db: AsyncSession) -> list[dict]:
    nic_rows = (
        await db.execute(
            select(AssetHwNic).where(
                AssetHwNic.asset_id == asset_id,
                AssetHwNic.is_unused.is_(True),
            )
        )
    ).scalars().all()

    return [
        {
            "adapter_name": nic.adapter_name,
            "connection_name": nic.connection_name,
            "mac_address": nic.mac_address,
            "ipv4_address": nic.ipv4_address,
        }
        for nic in nic_rows
    ]


async def _get_representative_account_signature(asset_id: int, db: AsyncSession) -> Optional[dict]:
    asset = await db.get(Asset, asset_id)
    if not asset or not asset.representative_account_id:
        return None

    account = await db.get(AssetSwAccount, asset.representative_account_id)
    if not account or account.asset_id != asset_id:
        return None

    return {
        "account_name": account.account_name,
        "comment": account.comment,
    }


def _remap_representative_nic(
    asset: Asset,
    nic_entities: list[AssetHwNic],
    previous_rep_nic: Optional[dict],
) -> None:
    if not nic_entities:
        asset.representative_nic_id = None
        return

    selected = None

    if previous_rep_nic:
        for nic in nic_entities:
            if previous_rep_nic.get("mac_address") and nic.mac_address == previous_rep_nic.get("mac_address"):
                selected = nic
                break
        if not selected:
            for nic in nic_entities:
                if (
                    previous_rep_nic.get("connection_name")
                    and previous_rep_nic.get("connection_name") == nic.connection_name
                ):
                    selected = nic
                    break
        if not selected:
            for nic in nic_entities:
                if previous_rep_nic.get("ipv4_address") and nic.ipv4_address == previous_rep_nic.get("ipv4_address"):
                    selected = nic
                    break

    if not selected and asset.representative_nic_id:
        selected = next((nic for nic in nic_entities if nic.id == asset.representative_nic_id), None)

    if selected:
        asset.representative_nic_id = selected.id
        return

    asset.representative_nic_id = None


def _remap_representative_account(
    asset: Asset,
    account_entities: list[AssetSwAccount],
    previous_rep_account: Optional[dict],
) -> None:
    if not account_entities:
        asset.representative_account_id = None
        return

    selected = None

    if previous_rep_account:
        for account in account_entities:
            if previous_rep_account.get("account_name") and account.account_name == previous_rep_account.get("account_name"):
                selected = account
                break
        if not selected:
            for account in account_entities:
                if previous_rep_account.get("comment") and account.comment == previous_rep_account.get("comment"):
                    selected = account
                    break

    if not selected and asset.representative_account_id:
        selected = next((account for account in account_entities if account.id == asset.representative_account_id), None)

    asset.representative_account_id = selected.id if selected else None


def _remap_unused_nics(asset: Asset, nic_entities: list[AssetHwNic], previous_unused_nics: list[dict]) -> None:
    selected_ids: set[int] = set()
    for signature in previous_unused_nics:
        matched = _match_nic_signature(nic_entities, signature)
        if matched and matched.id != asset.representative_nic_id:
            selected_ids.add(matched.id)

    for nic in nic_entities:
        nic.is_unused = nic.id in selected_ids


def _match_nic_signature(nic_entities: list[AssetHwNic], signature: Optional[dict]) -> Optional[AssetHwNic]:
    if not signature:
        return None

    if signature.get("mac_address"):
        for nic in nic_entities:
            if nic.mac_address == signature.get("mac_address"):
                return nic

    if signature.get("connection_name"):
        for nic in nic_entities:
            if nic.connection_name == signature.get("connection_name"):
                return nic

    if signature.get("ipv4_address"):
        for nic in nic_entities:
            if nic.ipv4_address == signature.get("ipv4_address"):
                return nic

    return None


def _normalize_collect_payload(data: dict) -> dict:
    meta_source = data.get("meta") or data.get("_meta") or {}
    normalized = {
        "meta": {
            "asset_code": meta_source.get("asset_code"),
            "hostname": meta_source.get("hostname"),
            "collected_at": meta_source.get("collected_at"),
            "collector_version": meta_source.get("collector_version") or meta_source.get("script_ver"),
            "source": meta_source.get("source") or "powershell",
        },
        "summary": {},
        "network": {
            "interfaces": [],
            "ip_addresses": [],
            "dns": [],
            "extra_addresses": [],
            "connections": [],
        },
        "software": [],
        "processes": [],
        "accounts": [],
        "hotfixes": [],
    }

    if "summary" in data:
        normalized["summary"] = {**normalized["summary"], **(data.get("summary") or {})}
    if "network" in data:
        network = data.get("network") or {}
        normalized["network"] = {
            "interfaces": _ensure_list(network.get("interfaces")),
            "ip_addresses": _ensure_list(network.get("ip_addresses")),
            "dns": _ensure_list(network.get("dns")),
            "extra_addresses": _ensure_list(network.get("extra_addresses")),
            "connections": _ensure_list(network.get("connections")),
        }
    if "software" in data:
        normalized["software"] = _ensure_list(data.get("software"))
    if "processes" in data:
        normalized["processes"] = _ensure_list(data.get("processes"))
    if "accounts" in data:
        normalized["accounts"] = _ensure_list(data.get("accounts"))
    if "hotfixes" in data:
        normalized["hotfixes"] = _ensure_list(data.get("hotfixes"))

    if "system" in data:
        sys_data = data["system"] or {}
        cs = _first_item(sys_data.get("csproduct"))
        os_info = _first_item(sys_data.get("os"))
        ci = _first_item(sys_data.get("computerinfo"))
        normalized["summary"].update({
            "manufacturer": cs.get("Vendor") or ci.get("CsManufacturer"),
            "model_name": cs.get("Name") or ci.get("CsModel"),
            "serial_number": cs.get("IdentifyingNumber"),
            "system_uuid": cs.get("UUID"),
            "os_name": os_info.get("Caption") or ci.get("OsName"),
            "os_version": os_info.get("Version") or ci.get("OsVersion"),
            "os_build": os_info.get("BuildNumber") or ci.get("OsBuildNumber"),
            "os_architecture": os_info.get("OSArchitecture") or ci.get("OsArchitecture"),
            "system_type": ci.get("CsSystemType"),
            "bios_version": ci.get("BiosSMBIOSBIOSVersion"),
            "memory_total": os_info.get("TotalVisibleMemorySize"),
            "hostname": meta_source.get("hostname"),
            "domain": ci.get("CsDomain"),
            "raw_csproduct": cs,
            "raw_os": os_info,
        })

    if "cpu" in data:
        items = _ensure_list(data.get("cpu"))
        normalized["summary"]["cpu_items"] = items
        if items and not normalized["summary"].get("cpu_model"):
            normalized["summary"]["cpu_model"] = items[0].get("Name")

    if "memory" in data:
        normalized["summary"]["memory_slots"] = [
            {
                "locator": item.get("DeviceLocator"),
                "capacity": item.get("Capacity"),
                "speed_mhz": item.get("Speed"),
                "manufacturer": item.get("Manufacturer"),
                "part_number": item.get("PartNumber"),
                "serial_number": item.get("SerialNumber"),
                "form_factor": item.get("FormFactor"),
                **item,
            }
            for item in _ensure_list(data.get("memory"))
        ]

    if "disk" in data:
        normalized["summary"]["disk_items"] = _ensure_list(data.get("disk"))

    if "gpu" in data:
        normalized["summary"]["gpu_items"] = _ensure_list(data.get("gpu"))

    if "nic" in data:
        normalized["network"]["interfaces"] = [
            {
                "name": item.get("InterfaceDescription"),
                "connection_name": item.get("InterfaceAlias"),
                "mac_address": item.get("MacAddress"),
                "ipv4_address": _extract_ip(item.get("IPv4Address")),
                "subnet_mask": item.get("SubnetMask"),
                "default_gateway": item.get("DefaultGateway"),
                "dns_servers": item.get("DNSServerSearchOrder") or item.get("DnsServers"),
                "dhcp_enabled": item.get("DHCPEnabled"),
                **item,
            }
            for item in _ensure_list(data.get("nic"))
        ]

    if "product" in data:
        normalized["software"] = [
            {
                "name": item.get("Name"),
                "version": item.get("Version"),
                "vendor": item.get("Vendor"),
                "installed_on": item.get("InstallDate"),
                **item,
            }
            for item in _ensure_list(data.get("product"))
            if item.get("Name")
        ]

    if "hotfix" in data:
        normalized["hotfixes"] = [
            {
                "hotfix_id": item.get("HotFixID"),
                "description": item.get("Description"),
                "installed_on": item.get("InstalledOn"),
                "installed_by": item.get("InstalledBy"),
                **item,
            }
            for item in _ensure_list(data.get("hotfix"))
        ]

    if "process" in data:
        normalized["processes"] = [
            {
                "name": item.get("ProcessName"),
                "pid": item.get("Id"),
                "session_name": item.get("SessionId"),
                "memory_kb": item.get("WorkingSetKB") or item.get("WorkingSet64"),
                **item,
            }
            for item in _ensure_list(data.get("process"))
        ]

    if "account" in data:
        normalized["accounts"] = [
            {
                "account_name": item.get("AccountName") or item.get("Name"),
                "enabled": item.get("Enabled"),
                "comment": item.get("Comment") or item.get("Description"),
                **item,
            }
            for item in _ensure_list(data.get("account"))
        ]

    if "connections" in data:
        normalized["network"]["connections"] = _normalize_connections(_ensure_list(data.get("connections")))

    return normalized


def _normalize_connections(items: list[dict]) -> list[dict]:
    rows = []
    for item in items:
        rows.append({
            "protocol": item.get("protocol") or item.get("Protocol"),
            "local_address": item.get("local_address") or item.get("LocalAddress"),
            "remote_address": item.get("remote_address") or item.get("RemoteAddress"),
            "state": item.get("state") or item.get("State"),
            "process_name": item.get("process_name") or item.get("ProcessName"),
            **item,
        })
    return rows


def _build_nic_rows(network_data: dict) -> list[dict]:
    interfaces = _ensure_list(network_data.get("interfaces"))
    ip_addresses = _ensure_list(network_data.get("ip_addresses"))

    if not interfaces and ip_addresses:
        return [
            {
                "adapter_name": None,
                "connection_name": None,
                "mac_address": None,
                "ipv4_address": item.get("ip"),
                "subnet_mask": _normalize_subnet_mask(item.get("subnet_mask")),
                "default_gateway": _string_or_none(item.get("gateway")),
                "dns_servers": _normalize_dns_servers(item.get("dns_servers") or item.get("dns")),
                "dhcp_enabled": item.get("dhcp_enabled"),
                "raw_json": item,
            }
            for item in ip_addresses
        ]

    rows = []
    for idx, item in enumerate(interfaces):
        ip_item = ip_addresses[idx] if idx < len(ip_addresses) else {}
        rows.append({
            "adapter_name": item.get("name") or item.get("adapter_name") or item.get("InterfaceDescription"),
            "connection_name": item.get("connection_name") or item.get("InterfaceAlias"),
            "mac_address": item.get("mac_address") or item.get("MacAddress"),
            "ipv4_address": item.get("ipv4_address") or item.get("ip") or ip_item.get("ip"),
            "subnet_mask": _normalize_subnet_mask(item.get("subnet_mask") or ip_item.get("subnet_mask")),
            "default_gateway": _string_or_none(item.get("default_gateway") or item.get("gateway") or ip_item.get("gateway")),
            "dns_servers": _normalize_dns_servers(item.get("dns_servers") or item.get("dns") or ip_item.get("dns_servers")),
            "dhcp_enabled": item.get("dhcp_enabled"),
            "raw_json": {**ip_item, **item},
        })
    return rows


def _first_item(val):
    if isinstance(val, list):
        return val[0] if val else {}
    return val or {}


def _first_ip_address(network_data: dict) -> Optional[str]:
    for item in _ensure_list(network_data.get("ip_addresses")):
        ip = item.get("ip")
        if ip:
            return ip
    for item in _ensure_list(network_data.get("interfaces")):
        ip = item.get("ipv4_address") or item.get("IPAddress")
        if ip:
            return _extract_ip(ip)
    return None


def _ensure_list(val) -> list:
    if val is None:
        return []
    if isinstance(val, list):
        return val
    return [val]


def _clean(val: Optional[str]) -> Optional[str]:
    if val is None:
        return None
    return str(val).strip() or None


def _bytes_to_mb(val) -> Optional[int]:
    if val is None:
        return None
    try:
        value = int(val)
        return value // (1024 * 1024) if value > 1_000_000 else value // 1024
    except (ValueError, TypeError):
        return None


def _memory_to_mb(val) -> Optional[int]:
    if val is None:
        return None
    try:
        value = str(val).strip().upper()
        if value.endswith("GB"):
            return int(float(value[:-2].strip()) * 1024)
        if value.endswith("MB"):
            return int(float(value[:-2].strip()))
        return _bytes_to_mb(val)
    except (ValueError, TypeError):
        return _bytes_to_mb(val)


def _parse_capacity_bytes(val) -> Optional[int]:
    if val is None:
        return None
    try:
        value = str(val).strip().upper()
        if value.endswith("GB"):
            return int(float(value[:-2].strip()) * 1024 * 1024 * 1024)
        if value.endswith("MB"):
            return int(float(value[:-2].strip()) * 1024 * 1024)
        return int(val)
    except (ValueError, TypeError):
        return None


def _arch_name(val) -> Optional[str]:
    arch_map = {0: "x86", 9: "x64", 5: "ARM", 12: "ARM64"}
    try:
        return arch_map.get(int(val), str(val))
    except Exception:
        return str(val) if val else None


def _parse_date(val):
    if val is None or val == "":
        return None
    try:
        s = str(val).replace("/", "-").strip()
        if len(s) == 8 and s.isdigit():
            return date(int(s[:4]), int(s[4:6]), int(s[6:8]))
        if "T" in s:
            return datetime.fromisoformat(s).date()
        return date.fromisoformat(s[:10])
    except Exception:
        return None


def _extract_ip(val) -> Optional[str]:
    if val is None:
        return None
    if isinstance(val, list):
        val = val[0] if val else None
    if isinstance(val, dict):
        val = val.get("IPAddress") or val.get("ip")
    return str(val).strip() if val else None


def _string_or_none(val) -> Optional[str]:
    if val is None or val == "":
        return None
    return str(val).strip()


def _normalize_subnet_mask(val) -> Optional[str]:
    if val is None or val == "":
        return None

    if isinstance(val, int):
        return _prefix_length_to_mask(val)

    text = str(val).strip()
    if not text:
        return None
    if text.isdigit():
        return _prefix_length_to_mask(int(text))
    return text


def _normalize_dns_servers(val) -> Optional[str]:
    if val is None or val == "":
        return None
    if isinstance(val, list):
        items = [str(item).strip() for item in val if str(item).strip()]
        return ", ".join(items) or None
    text = str(val).strip()
    if not text:
        return None
    if ";" in text:
        return ", ".join(part.strip() for part in text.split(";") if part.strip()) or None
    return text


def _to_bool(val) -> Optional[bool]:
    if val is None or val == "":
        return None
    if isinstance(val, bool):
        return val
    text = str(val).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n"}:
        return False
    return None


def _dedupe_gpu_items(items: list[dict]) -> list[dict]:
    seen = set()
    deduped = []
    for item in items:
        key = (
            _clean(item.get("name") or item.get("Name")),
            _clean(item.get("driver_version") or item.get("DriverVersion")),
            _clean(item.get("resolution") or item.get("VideoModeDescription")),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _prefix_length_to_mask(prefix: int) -> Optional[str]:
    if prefix < 0 or prefix > 32:
        return None
    bits = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
    return ".".join(str((bits >> shift) & 0xFF) for shift in (24, 16, 8, 0))


def _parse_datetime(val) -> datetime:
    if val is None:
        return datetime.now()
    if isinstance(val, datetime):
        return val
    try:
        return datetime.fromisoformat(str(val))
    except (ValueError, TypeError):
        return datetime.now()
