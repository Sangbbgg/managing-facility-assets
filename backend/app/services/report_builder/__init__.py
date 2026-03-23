from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession


async def build_report(report_type: str, date_from: date, date_to: date, db: AsyncSession) -> str:
    match report_type:
        case "형상관리대장":     from .asset_config import build
        case "설비관리대장":     from .asset_mgmt import build
        case "예방점검_월간":    from .inspection_monthly import build
        case "예방점검_분기":    from .inspection_quarterly import build
        case "이벤트로그":       from .event_log import build
        case "콘솔접속대장":     from .console_access import build
        case "봉인지관리대장":   from .seal import build
        case "비밀번호관리대장": from .password import build
        case _: raise ValueError(f"알 수 없는 보고서 타입: {report_type}")
    return await build(date_from, date_to, db)
