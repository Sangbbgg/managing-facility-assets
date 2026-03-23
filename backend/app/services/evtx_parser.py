from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import defaultdict
from pathlib import Path

TARGET_LEVELS = {1, 2, 3}  # Critical=1, Error=2, Warning=3
NS = "http://schemas.microsoft.com/win/2004/08/events/event"


def _parse_single_file(evtx_path: str) -> list[dict]:
    """최상위 함수 필수 — ProcessPoolExecutor pickle 요건"""
    from Evtx.Evtx import Evtx
    from lxml import etree

    records = []
    with Evtx(evtx_path) as log:
        for record in log.records():
            try:
                root = etree.fromstring(record.xml().encode("utf-8"))
                sys_el = root.find(f"{{{NS}}}System")
                if sys_el is None:
                    continue
                level_el = sys_el.find(f"{{{NS}}}Level")
                try:
                    level = int(level_el.text) if level_el is not None else -1
                except (ValueError, TypeError):
                    level = -1
                if level not in TARGET_LEVELS:
                    continue
                eid_el = sys_el.find(f"{{{NS}}}EventID")
                ts_el  = sys_el.find(f"{{{NS}}}TimeCreated")
                records.append({
                    "event_id":  int(eid_el.text) if eid_el is not None else -1,
                    "level":     level,
                    "timestamp": ts_el.get("SystemTime", "") if ts_el is not None else "",
                })
            except Exception:
                continue
    return records


async def parse_evtx_directory(base_dir: Path, asset_id: int, record_date, db) -> int:
    from app.models.record import EventLogRecord

    evtx_files = list(base_dir.rglob("*.evtx"))
    if not evtx_files:
        return 0

    all_records: list[dict] = []
    with ProcessPoolExecutor() as pool:
        futures = {pool.submit(_parse_single_file, str(f)): f for f in evtx_files}
        for future in as_completed(futures):
            try:
                all_records.extend(future.result())
            except Exception as e:
                print(f"[evtx 오류] {futures[future].name}: {e}")

    counts: dict[tuple, int] = defaultdict(int)
    for r in all_records:
        counts[(r["event_id"], r["level"])] += 1

    for (event_id, level), count in counts.items():
        db.add(EventLogRecord(
            asset_id=asset_id,
            record_date=record_date,
            log_type="sys",
            event_id=event_id,
            level=level,
            count=count,
        ))
    await db.flush()
    return len(counts)
