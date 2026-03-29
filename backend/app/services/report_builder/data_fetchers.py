from typing import Optional
from sqlalchemy import select, extract
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.asset import Asset
from app.models.hw_info import AssetHwNic
from app.models.sw_info import AssetSwAccount
from app.models.master import (
    GroupNode, LocationNode, EquipmentType, Person,
)
from app.models.record import (
    InspectionRecord, EventLogRecord,
    ConsoleAccessRecord, SealRecord, PasswordRecord,
)


def _d(val) -> str:
    """날짜/datetime → 문자열"""
    if val is None:
        return ""
    if hasattr(val, "date"):
        return str(val.date())
    return str(val)


async def _load_masters(db: AsyncSession):
    groups   = {r.id: r for r in (await db.execute(select(GroupNode))).scalars()}
    locs     = {r.id: r for r in (await db.execute(select(LocationNode))).scalars()}
    eq_types = {r.id: r for r in (await db.execute(select(EquipmentType))).scalars()}
    persons  = {r.id: r for r in (await db.execute(select(Person))).scalars()}
    nics = {r.id: r for r in (await db.execute(select(AssetHwNic))).scalars()}
    accounts = {r.id: r for r in (await db.execute(select(AssetSwAccount))).scalars()}
    return groups, locs, eq_types, persons, nics, accounts


def _asset_ip(asset, nics) -> str:
    if asset.representative_nic_id and asset.representative_nic_id in nics:
        nic = nics[asset.representative_nic_id]
        if not nic.is_unused:
            return nic.ipv4_address or ""
    return ""


def _asset_ips(asset, nics) -> list[str]:
    return [
        nic.ipv4_address
        for nic in nics.values()
        if nic.asset_id == asset.id and nic.ipv4_address and not nic.is_unused
    ]


def _used_ips(asset, asset_nics) -> list[str]:
    return [
        nic.ipv4_address
        for nic in asset_nics
        if nic.ipv4_address and nic.id != asset.representative_nic_id and not nic.is_unused
    ]


def _unused_ips(asset_nics) -> list[str]:
    return [
        nic.ipv4_address
        for nic in asset_nics
        if nic.ipv4_address and nic.is_unused
    ]


def _active_ips(asset, nics, asset_nics) -> list[str]:
    values: list[str] = []
    representative_ip = _asset_ip(asset, nics)
    if representative_ip:
        values.append(representative_ip)
    values.extend(_used_ips(asset, asset_nics))
    return values


def _asset_row(a, groups, locs, eq_types, persons, nics, accounts) -> dict:
    grp      = groups.get(a.group_id)
    loc      = locs.get(a.location_id)
    eq       = eq_types.get(a.equipment_type_id)
    mgr      = persons.get(a.manager_id)
    asset_nics = [nic for nic in nics.values() if nic.asset_id == a.id]
    representative_nic = next(
        (nic for nic in asset_nics if a.representative_nic_id and nic.id == a.representative_nic_id),
        None,
    )
    used_nics = [
        _nic_label(nic)
        for nic in asset_nics
        if nic.id != a.representative_nic_id and not nic.is_unused
    ]
    unused_nics = [
        _nic_label(nic)
        for nic in asset_nics
        if nic.is_unused
    ]
    representative_account = accounts.get(a.representative_account_id) if a.representative_account_id else None
    local_accounts = [
        account.account_name
        for account in accounts.values()
        if account.asset_id == a.id and account.account_name and account.enabled is not False
    ]
    disabled_accounts = [
        account.account_name
        for account in accounts.values()
        if account.asset_id == a.id and account.account_name and account.enabled is False
    ]
    return {
        "id":                  a.id,
        "asset_code":          a.asset_code or "",
        "asset_name":          a.asset_name or "",
        "active_ip_addresses": _active_ips(a, nics, asset_nics),
        "unused_ip_addresses": _unused_ips(asset_nics),
        "custom_fields_json":  a.custom_fields_json or {},
        "purpose":             a.purpose or "",
        "importance":          a.importance or "",
        "status":              a.status or "",
        "install_date":        _d(a.install_date),
        "created_at":          _d(a.created_at),
        "updated_at":          _d(a.updated_at),
        "last_collected_at":   _d(a.last_collected_at),
        "group_name":          grp.name if grp else "",
        "group_full_path":     grp.full_path if grp else "",
        "group_code":          (grp.code or "") if grp else "",
        "location_name":       loc.name if loc else "",
        "location_full_path":  loc.full_path if loc else "",
        "equipment_type_name": eq.name if eq else "",
        "equipment_type_code": eq.code if eq else "",
        "representative_nic_name": _nic_label(representative_nic) if representative_nic else "",
        "used_nic_names":      used_nics,
        "unused_nic_names":    unused_nics,
        "manager_name":        mgr.name if mgr else "",
        "manager_title":       (mgr.title or "") if mgr else "",
        "manager_contact":     (mgr.contact or "") if mgr else "",
        "representative_account_name": representative_account.account_name if representative_account else "",
        "local_account_names": local_accounts,
        "disabled_account_names": disabled_accounts,
    }


def _nic_label(nic) -> str:
    if not nic:
        return ""
    return " ".join(
        part
        for part in [
            nic.connection_name or nic.adapter_name,
            f"({nic.mac_address})" if nic.mac_address else "",
            f"- {nic.ipv4_address}" if nic.ipv4_address else "",
        ]
        if part
    )


async def fetch_asset_rows(year: int, month: Optional[int], db: AsyncSession) -> list[dict]:
    """형상관리대장 / 설비관리대장 — 전체 현재 자산 (시기는 헤더 라벨 용도)"""
    masters = await _load_masters(db)
    stmt = select(Asset).where(Asset.is_deleted == False).order_by(Asset.asset_code)
    assets = (await db.execute(stmt)).scalars().all()
    return [_asset_row(a, *masters) for a in assets]


async def fetch_inspection_rows(year: int, month: Optional[int], db: AsyncSession, insp_type: str) -> list[dict]:
    masters = await _load_masters(db)
    groups, locs, _, _, nics, _ = masters

    conds = [
        InspectionRecord.inspection_type == insp_type,
        extract("year", InspectionRecord.record_date) == year,
    ]
    if month:
        conds.append(extract("month", InspectionRecord.record_date) == month)

    stmt = (
        select(InspectionRecord, Asset)
        .join(Asset, InspectionRecord.asset_id == Asset.id)
        .where(*conds)
        .order_by(InspectionRecord.record_date, Asset.asset_code)
    )
    rows = []
    for rec, a in (await db.execute(stmt)).all():
        grp = groups.get(a.group_id)
        loc = locs.get(a.location_id)
        q = ((rec.record_date.month - 1) // 3) + 1
        sheet_key = (
            rec.record_date.strftime("%Y년 %m월")
            if insp_type == "MONTHLY"
            else f"{year}년 {q}분기"
        )
        rows.append({
            "_sheet_key":       sheet_key,
            "asset_code":       a.asset_code or "",
            "asset_name":       a.asset_name or "",
            "group_name":       grp.name if grp else "",
            "location_full_path": loc.full_path if loc else "",
            "ip_address":       _asset_ip(a, nics),
            "record_date":      _d(rec.record_date),
            "inspection_type":  rec.inspection_type,
            "result":           rec.result or "",
            "inspector":        rec.inspector or "",
            "special_notes":    rec.special_notes or "",
        })
    return rows


async def fetch_event_log_rows(year: int, month: Optional[int], db: AsyncSession) -> list[dict]:
    masters = await _load_masters(db)
    groups, locs, _, _, nics, _ = masters
    LEVEL_MAP = {1: "Critical", 2: "Error", 3: "Warning"}

    conds = [extract("year", EventLogRecord.record_date) == year]
    if month:
        conds.append(extract("month", EventLogRecord.record_date) == month)

    stmt = (
        select(EventLogRecord, Asset)
        .join(Asset, EventLogRecord.asset_id == Asset.id)
        .where(*conds)
        .order_by(EventLogRecord.record_date, Asset.asset_code)
    )
    rows = []
    for rec, a in (await db.execute(stmt)).all():
        grp = groups.get(a.group_id)
        loc = locs.get(a.location_id)
        rows.append({
            "_sheet_key":       rec.record_date.strftime("%Y년 %m월"),
            "asset_code":       a.asset_code or "",
            "asset_name":       a.asset_name or "",
            "group_name":       grp.name if grp else "",
            "location_full_path": loc.full_path if loc else "",
            "ip_address":       _asset_ip(a, nics),
            "record_date":      _d(rec.record_date),
            "log_type":         rec.log_type,
            "event_id":         str(rec.event_id),
            "level":            LEVEL_MAP.get(rec.level, str(rec.level)),
            "count":            str(rec.count),
        })
    return rows


async def fetch_console_rows(year: int, month: Optional[int], db: AsyncSession) -> list[dict]:
    masters = await _load_masters(db)
    groups, locs, _, _, nics, _ = masters

    conds = [extract("year", ConsoleAccessRecord.access_date) == year]
    if month:
        conds.append(extract("month", ConsoleAccessRecord.access_date) == month)

    stmt = (
        select(ConsoleAccessRecord, Asset)
        .join(Asset, ConsoleAccessRecord.asset_id == Asset.id)
        .where(*conds)
        .order_by(ConsoleAccessRecord.access_date, Asset.asset_code)
    )
    rows = []
    for rec, a in (await db.execute(stmt)).all():
        grp = groups.get(a.group_id)
        loc = locs.get(a.location_id)
        rows.append({
            "asset_code":         a.asset_code or "",
            "asset_name":         a.asset_name or "",
            "group_name":         grp.name if grp else "",
            "location_full_path": loc.full_path if loc else "",
            "ip_address":         _asset_ip(a, nics),
            "access_date":        _d(rec.access_date),
            "accessor":           rec.accessor or "",
            "purpose":            rec.purpose or "",
        })
    return rows


async def fetch_seal_rows(year: int, month: Optional[int], db: AsyncSession) -> list[dict]:
    masters = await _load_masters(db)
    groups, locs, _, _, nics, _ = masters

    conds = [extract("year", SealRecord.record_date) == year]
    if month:
        conds.append(extract("month", SealRecord.record_date) == month)

    stmt = (
        select(SealRecord, Asset)
        .join(Asset, SealRecord.asset_id == Asset.id)
        .where(*conds)
        .order_by(SealRecord.record_date, Asset.asset_code)
    )
    rows = []
    for rec, a in (await db.execute(stmt)).all():
        grp = groups.get(a.group_id)
        loc = locs.get(a.location_id)
        rows.append({
            "asset_code":         a.asset_code or "",
            "asset_name":         a.asset_name or "",
            "group_name":         grp.name if grp else "",
            "location_full_path": loc.full_path if loc else "",
            "ip_address":         _asset_ip(a, nics),
            "record_date":        _d(rec.record_date),
            "seal_number":        rec.seal_number or "",
            "action":             rec.action or "",
            "handler":            rec.handler or "",
            "notes":              rec.notes or "",
        })
    return rows


async def fetch_password_rows(year: int, month: Optional[int], db: AsyncSession) -> list[dict]:
    masters = await _load_masters(db)
    groups, locs, _, _, nics, _ = masters

    conds = [extract("year", PasswordRecord.changed_date) == year]
    if month:
        conds.append(extract("month", PasswordRecord.changed_date) == month)

    stmt = (
        select(PasswordRecord, Asset)
        .join(Asset, PasswordRecord.asset_id == Asset.id)
        .where(*conds)
        .order_by(PasswordRecord.changed_date, Asset.asset_code)
    )
    rows = []
    for rec, a in (await db.execute(stmt)).all():
        grp = groups.get(a.group_id)
        loc = locs.get(a.location_id)
        rows.append({
            "asset_code":         a.asset_code or "",
            "asset_name":         a.asset_name or "",
            "group_name":         grp.name if grp else "",
            "location_full_path": loc.full_path if loc else "",
            "ip_address":         _asset_ip(a, nics),
            "account_name":       rec.account_name or "",
            "changed_date":       _d(rec.changed_date),
            "changed_by":         rec.changed_by or "",
            "notes":              rec.notes or "",
        })
    return rows


async def fetch_rows(data_source: str, year: int, month: Optional[int], db: AsyncSession) -> list[dict]:
    match data_source:
        case "형상관리대장" | "설비관리대장":
            return await fetch_asset_rows(year, month, db)
        case "예방점검_월간":
            return await fetch_inspection_rows(year, month, db, "MONTHLY")
        case "예방점검_분기":
            return await fetch_inspection_rows(year, month, db, "QUARTERLY")
        case "이벤트로그":
            return await fetch_event_log_rows(year, month, db)
        case "콘솔접속대장":
            return await fetch_console_rows(year, month, db)
        case "봉인지관리대장":
            return await fetch_seal_rows(year, month, db)
        case "비밀번호관리대장":
            return await fetch_password_rows(year, month, db)
        case _:
            raise ValueError(f"알 수 없는 data_source: {data_source}")
