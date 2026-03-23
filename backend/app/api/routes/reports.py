from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.core.database import get_db
from app.models.report import ReportTemplate
from app.schemas.report import ReportTemplateCreate, ReportTemplateRead, ReportTemplateUpdate
from app.services.report_builder import build_report
from app.services.report_builder.field_catalog import FIELD_CATALOG, DATA_SOURCES

router = APIRouter()


# ── 데이터소스 목록 ────────────────────────────────────────────

@router.get("/data-sources")
async def get_data_sources():
    return DATA_SOURCES


# ── 필드 카탈로그 ──────────────────────────────────────────────

@router.get("/fields/{data_source}")
async def get_fields(data_source: str):
    if data_source not in FIELD_CATALOG:
        raise HTTPException(404, f"알 수 없는 data_source: {data_source}")
    return FIELD_CATALOG[data_source]


# ── 서식 CRUD ─────────────────────────────────────────────────

@router.get("/templates", response_model=list[ReportTemplateRead])
async def list_templates(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ReportTemplate).order_by(ReportTemplate.id))
    return result.scalars().all()


@router.post("/templates", response_model=ReportTemplateRead, status_code=201)
async def create_template(body: ReportTemplateCreate, db: AsyncSession = Depends(get_db)):
    if body.data_source not in DATA_SOURCES:
        raise HTTPException(400, f"유효하지 않은 data_source: {body.data_source}")
    row = ReportTemplate(**body.model_dump())
    db.add(row)
    await db.flush()
    await db.refresh(row)
    return row


@router.get("/templates/{tmpl_id}", response_model=ReportTemplateRead)
async def get_template(tmpl_id: int, db: AsyncSession = Depends(get_db)):
    row = await db.get(ReportTemplate, tmpl_id)
    if not row:
        raise HTTPException(404, "서식을 찾을 수 없습니다")
    return row


@router.patch("/templates/{tmpl_id}", response_model=ReportTemplateRead)
async def update_template(tmpl_id: int, body: ReportTemplateUpdate, db: AsyncSession = Depends(get_db)):
    row = await db.get(ReportTemplate, tmpl_id)
    if not row:
        raise HTTPException(404, "서식을 찾을 수 없습니다")
    data = body.model_dump(exclude_unset=True)
    if "data_source" in data and data["data_source"] not in DATA_SOURCES:
        raise HTTPException(400, "유효하지 않은 data_source")
    for k, v in data.items():
        setattr(row, k, v)
    await db.flush()
    await db.refresh(row)
    return row


@router.delete("/templates/{tmpl_id}", status_code=204)
async def delete_template(tmpl_id: int, db: AsyncSession = Depends(get_db)):
    row = await db.get(ReportTemplate, tmpl_id)
    if row:
        await db.delete(row)


# ── 보고서 생성 ────────────────────────────────────────────────

@router.post("/generate")
async def generate_report(
    template_id: int = Query(...),
    year: int = Query(...),
    month: Optional[int] = Query(None, ge=1, le=12),
    db: AsyncSession = Depends(get_db),
):
    try:
        file_path = await build_report(template_id, year, month, db)
    except ValueError as e:
        raise HTTPException(400, str(e))

    template = await db.get(ReportTemplate, template_id)
    month_str = f"_{month:02d}월" if month else "_전체"
    filename = f"{template.display_name}_{year}년{month_str}.xlsx"
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
