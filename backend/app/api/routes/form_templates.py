from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sa_func
from typing import Optional
from pathlib import Path
import shutil

from app.core.database import get_db
from app.models.form_template import ReportFormTemplate, ReportFormMapping
from app.schemas.form_template import (
    FormTemplateUpdate, FormTemplateRead,
    FormMappingCreate, FormMappingUpdate, FormMappingRead,
    FormMappingBulkSave, FormFieldInfo,
)

router = APIRouter()

TEMPLATE_DIR = Path("/app/data/form_templates")
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)


# ─── 필드 카탈로그 (매핑 편집 UI용) — 경로 충돌 방지: 최상단에 위치 ───

@router.get("/field-catalog", response_model=list[FormFieldInfo])
async def get_field_catalog():
    from app.services.form_report_builder import FIELD_CATALOG
    return FIELD_CATALOG


# ─── 양식 보고서 생성 ───

@router.post("/generate")
async def generate_form_report(
    template_id: int = Query(...),
    asset_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    from app.services.form_report_builder import generate_form_report as _gen
    file_path, file_name = await _gen(template_id, asset_id, db)
    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# ─── 웹 미리보기 ───

@router.post("/preview")
async def preview_form_report(
    template_id: int = Query(...),
    asset_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    from app.services.form_report_preview import generate_preview_html
    html = await generate_preview_html(template_id, asset_id, db)
    return {"html": html}


# ─── 양식 템플릿 CRUD ───

@router.get("", response_model=list[FormTemplateRead])
async def list_templates(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(ReportFormTemplate)
    if category:
        stmt = stmt.where(ReportFormTemplate.category == category)
    if is_active is not None:
        stmt = stmt.where(ReportFormTemplate.is_active == is_active)
    stmt = stmt.order_by(ReportFormTemplate.created_at.desc())
    rows = (await db.execute(stmt)).scalars().all()

    result = []
    for t in rows:
        count_stmt = select(sa_func.count()).where(ReportFormMapping.template_id == t.id)
        count = (await db.execute(count_stmt)).scalar() or 0
        d = FormTemplateRead.model_validate(t)
        d.mapping_count = count
        result.append(d)
    return result


@router.post("", response_model=FormTemplateRead)
async def create_template(
    name: str = Form(...),
    description: str = Form(None),
    category: str = Form("general"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(400, "xlsx 또는 xls 파일만 업로드 가능합니다")

    template = ReportFormTemplate(
        name=name,
        description=description,
        file_name=file.filename,
        file_path="",
        category=category,
    )
    db.add(template)
    await db.flush()

    safe_name = f"{template.id}_{file.filename}"
    save_path = TEMPLATE_DIR / safe_name
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    template.file_path = str(save_path)
    await db.commit()
    await db.refresh(template)

    return FormTemplateRead.model_validate(template)


@router.get("/{template_id}", response_model=FormTemplateRead)
async def get_template(template_id: int, db: AsyncSession = Depends(get_db)):
    t = await db.get(ReportFormTemplate, template_id)
    if not t:
        raise HTTPException(404, "양식을 찾을 수 없습니다")
    return FormTemplateRead.model_validate(t)


@router.get("/{template_id}/file")
async def download_template_file(template_id: int, db: AsyncSession = Depends(get_db)):
    t = await db.get(ReportFormTemplate, template_id)
    if not t:
        raise HTTPException(404, "template not found")
    return FileResponse(
        path=t.file_path,
        filename=t.file_name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.patch("/{template_id}", response_model=FormTemplateRead)
async def update_template(
    template_id: int,
    body: FormTemplateUpdate,
    db: AsyncSession = Depends(get_db),
):
    t = await db.get(ReportFormTemplate, template_id)
    if not t:
        raise HTTPException(404)
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(t, k, v)
    await db.commit()
    await db.refresh(t)
    return FormTemplateRead.model_validate(t)


@router.delete("/{template_id}")
async def delete_template(template_id: int, db: AsyncSession = Depends(get_db)):
    t = await db.get(ReportFormTemplate, template_id)
    if not t:
        raise HTTPException(404)
    p = Path(t.file_path)
    if p.exists():
        p.unlink()
    await db.delete(t)
    await db.commit()
    return {"ok": True}


# ─── 매핑 CRUD ───

@router.get("/{template_id}/mappings", response_model=list[FormMappingRead])
async def list_mappings(template_id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(ReportFormMapping)
        .where(ReportFormMapping.template_id == template_id)
        .order_by(ReportFormMapping.sort_order)
    )
    return (await db.execute(stmt)).scalars().all()


@router.post("/{template_id}/mappings", response_model=FormMappingRead)
async def create_mapping(
    template_id: int,
    body: FormMappingCreate,
    db: AsyncSession = Depends(get_db),
):
    m = ReportFormMapping(template_id=template_id, **body.model_dump())
    db.add(m)
    await db.commit()
    await db.refresh(m)
    return m


@router.put("/{template_id}/mappings/bulk", response_model=list[FormMappingRead])
async def bulk_save_mappings(
    template_id: int,
    body: FormMappingBulkSave,
    db: AsyncSession = Depends(get_db),
):
    del_stmt = select(ReportFormMapping).where(ReportFormMapping.template_id == template_id)
    existing = (await db.execute(del_stmt)).scalars().all()
    for e in existing:
        await db.delete(e)
    await db.flush()

    result = []
    for item in body.mappings:
        m = ReportFormMapping(template_id=template_id, **item.model_dump())
        db.add(m)
        await db.flush()
        await db.refresh(m)
        result.append(m)
    await db.commit()
    return result


@router.patch("/{template_id}/mappings/{mapping_id}", response_model=FormMappingRead)
async def update_mapping(
    template_id: int,
    mapping_id: int,
    body: FormMappingUpdate,
    db: AsyncSession = Depends(get_db),
):
    m = await db.get(ReportFormMapping, mapping_id)
    if not m or m.template_id != template_id:
        raise HTTPException(404)
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(m, k, v)
    await db.commit()
    await db.refresh(m)
    return m


@router.delete("/{template_id}/mappings/{mapping_id}")
async def delete_mapping(
    template_id: int,
    mapping_id: int,
    db: AsyncSession = Depends(get_db),
):
    m = await db.get(ReportFormMapping, mapping_id)
    if not m or m.template_id != template_id:
        raise HTTPException(404)
    await db.delete(m)
    await db.commit()
    return {"ok": True}


# ─── 템플릿 xlsx 구조 분석 ───

@router.get("/{template_id}/analyze")
async def analyze_template(template_id: int, db: AsyncSession = Depends(get_db)):
    from app.services.form_report_preview import analyze_template_structure
    t = await db.get(ReportFormTemplate, template_id)
    if not t:
        raise HTTPException(404)
    return await analyze_template_structure(t.file_path)


@router.get("/{template_id}/workbook-preview")
async def preview_template_workbook(template_id: int, db: AsyncSession = Depends(get_db)):
    from app.services.form_report_preview import generate_template_workbook_preview

    t = await db.get(ReportFormTemplate, template_id)
    if not t:
        raise HTTPException(404, "template not found")
    return await generate_template_workbook_preview(t.file_path)
