from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from app.core.database import get_db
from app.services.report_builder import build_report

router = APIRouter()

REPORT_TYPES = [
    "형상관리대장", "설비관리대장",
    "예방점검_월간", "예방점검_분기",
    "이벤트로그", "콘솔접속대장",
    "봉인지관리대장", "비밀번호관리대장",
]

@router.post("/generate")
async def generate_report(
    report_type: str = Query(..., enum=REPORT_TYPES),
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: AsyncSession = Depends(get_db),
):
    if date_from > date_to:
        raise HTTPException(400, "시작일이 종료일보다 늦을 수 없습니다")
    file_path = await build_report(report_type, date_from, date_to, db)
    filename = f"{report_type}_{date_from}_{date_to}.xlsx"
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
