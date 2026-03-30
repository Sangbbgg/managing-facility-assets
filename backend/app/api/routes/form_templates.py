from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sa_func
from sqlalchemy.orm import selectinload
from typing import Optional
from pathlib import Path
import shutil

from app.core.database import get_db
from app.models.form_template import ReportFormTemplateFolder, ReportFormTemplate, ReportFormMapping
from app.schemas.form_template import (
    FormTemplateFolderCreate, FormTemplateFolderRead, FormTemplateFolderUpdate,
    FormTemplateUpdate, FormTemplateRead,
    FormMappingCreate, FormMappingUpdate, FormMappingRead,
    FormMappingBulkSave, FormFieldInfo,
)

router = APIRouter()

TEMPLATE_DIR = Path("/app/data/form_templates")
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)


def _serialize_template(template: ReportFormTemplate, mapping_count: int = 0) -> FormTemplateRead:
    folder_name = template.folder.name if getattr(template, "folder", None) else None
    folder_path = f"{folder_name} > {template.file_name}" if folder_name else template.file_name
    return FormTemplateRead(
        id=template.id,
        name=template.name,
        description=template.description,
        file_name=template.file_name,
        category=template.category,
        folder_id=template.folder_id,
        folder_name=folder_name,
        folder_path=folder_path,
        is_active=template.is_active,
        created_at=template.created_at,
        updated_at=template.updated_at,
        mapping_count=mapping_count,
    )


# ─── 필드 카탈로그 (매핑 편집 UI용) — 경로 충돌 방지: 최상단에 위치 ───

@router.get("/field-catalog", response_model=list[FormFieldInfo])
async def get_field_catalog():
    from app.services.form_report_builder import FIELD_CATALOG
    return FIELD_CATALOG


@router.get("/folders", response_model=list[FormTemplateFolderRead])
async def list_template_folders(db: AsyncSession = Depends(get_db)):
    stmt = select(ReportFormTemplateFolder).order_by(ReportFormTemplateFolder.name.asc())
    return (await db.execute(stmt)).scalars().all()


@router.post("/folders", response_model=FormTemplateFolderRead)
async def create_template_folder(body: FormTemplateFolderCreate, db: AsyncSession = Depends(get_db)):
    name = body.name.strip()
    if not name:
        raise HTTPException(400, "폴더명을 입력하세요")

    exists = await db.scalar(
        select(ReportFormTemplateFolder.id).where(ReportFormTemplateFolder.name == name)
    )
    if exists:
        raise HTTPException(400, "같은 이름의 폴더가 이미 있습니다")

    folder = ReportFormTemplateFolder(name=name)
    db.add(folder)
    await db.commit()
    await db.refresh(folder)
    return folder


@router.patch("/folders/{folder_id}", response_model=FormTemplateFolderRead)
async def update_template_folder(
    folder_id: int,
    body: FormTemplateFolderUpdate,
    db: AsyncSession = Depends(get_db),
):
    folder = await db.get(ReportFormTemplateFolder, folder_id)
    if not folder:
        raise HTTPException(404, "폴더를 찾을 수 없습니다")

    name = body.name.strip()
    if not name:
        raise HTTPException(400, "폴더명을 입력하세요")

    exists = await db.scalar(
        select(ReportFormTemplateFolder.id)
        .where(ReportFormTemplateFolder.name == name, ReportFormTemplateFolder.id != folder_id)
    )
    if exists:
        raise HTTPException(400, "같은 이름의 폴더가 이미 있습니다")

    folder.name = name
    await db.commit()
    await db.refresh(folder)
    return folder


@router.delete("/folders/{folder_id}")
async def delete_template_folder(folder_id: int, db: AsyncSession = Depends(get_db)):
    folder = await db.get(
        ReportFormTemplateFolder,
        folder_id,
        options=[selectinload(ReportFormTemplateFolder.templates)],
    )
    if not folder:
        raise HTTPException(404, "폴더를 찾을 수 없습니다")
    if folder.templates:
        raise HTTPException(400, "템플릿이 남아 있는 폴더는 삭제할 수 없습니다")

    await db.delete(folder)
    await db.commit()
    return {"ok": True}


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
    stmt = select(ReportFormTemplate).options(selectinload(ReportFormTemplate.folder))
    if category:
        stmt = stmt.where(ReportFormTemplate.category == category)
    if is_active is not None:
        stmt = stmt.where(ReportFormTemplate.is_active == is_active)
    stmt = stmt.order_by(ReportFormTemplate.folder_id.asc().nullsfirst(), ReportFormTemplate.name.asc())
    rows = (await db.execute(stmt)).scalars().all()

    result = []
    for t in rows:
        count_stmt = select(sa_func.count()).where(ReportFormMapping.template_id == t.id)
        count = (await db.execute(count_stmt)).scalar() or 0
        result.append(_serialize_template(t, count))
    return result


@router.post("", response_model=FormTemplateRead)
async def create_template(
    name: str = Form(...),
    description: str = Form(None),
    category: str = Form("general"),
    folder_id: Optional[int] = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(400, "xlsx 또는 xls 파일만 업로드 가능합니다")

    if folder_id is not None:
        folder = await db.get(ReportFormTemplateFolder, folder_id)
        if not folder:
            raise HTTPException(400, "선택한 폴더를 찾을 수 없습니다")

    template = ReportFormTemplate(
        name=name,
        description=description,
        file_name=file.filename,
        file_path="",
        category=category,
        folder_id=folder_id,
    )
    db.add(template)
    await db.flush()

    safe_name = f"{template.id}_{file.filename}"
    save_path = TEMPLATE_DIR / safe_name
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    template.file_path = str(save_path)
    await db.commit()
    row = (
        await db.execute(
            select(
                ReportFormTemplate.id,
                ReportFormTemplate.name,
                ReportFormTemplate.description,
                ReportFormTemplate.file_name,
                ReportFormTemplate.category,
                ReportFormTemplate.folder_id,
                ReportFormTemplate.is_active,
                ReportFormTemplate.created_at,
                ReportFormTemplate.updated_at,
                ReportFormTemplateFolder.name.label("folder_name"),
            )
            .outerjoin(
                ReportFormTemplateFolder,
                ReportFormTemplate.folder_id == ReportFormTemplateFolder.id,
            )
            .where(ReportFormTemplate.id == template.id)
        )
    ).mappings().first()

    if not row:
        raise HTTPException(500, "템플릿 저장 후 조회에 실패했습니다")

    folder_name = row["folder_name"]
    folder_path = f"{folder_name} > {row['file_name']}" if folder_name else row["file_name"]
    return FormTemplateRead(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        file_name=row["file_name"],
        category=row["category"],
        folder_id=row["folder_id"],
        folder_name=folder_name,
        folder_path=folder_path,
        is_active=row["is_active"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        mapping_count=0,
    )


@router.get("/{template_id}", response_model=FormTemplateRead)
async def get_template(template_id: int, db: AsyncSession = Depends(get_db)):
    t = await db.get(ReportFormTemplate, template_id, options=[selectinload(ReportFormTemplate.folder)])
    if not t:
        raise HTTPException(404, "양식을 찾을 수 없습니다")
    count_stmt = select(sa_func.count()).where(ReportFormMapping.template_id == t.id)
    count = (await db.execute(count_stmt)).scalar() or 0
    return _serialize_template(t, count)


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
    t = await db.get(ReportFormTemplate, template_id, options=[selectinload(ReportFormTemplate.folder)])
    if not t:
        raise HTTPException(404)
    if body.folder_id is not None:
        folder = await db.get(ReportFormTemplateFolder, body.folder_id)
        if not folder:
            raise HTTPException(400, "선택한 폴더를 찾을 수 없습니다")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(t, k, v)
    await db.commit()
    await db.refresh(t, attribute_names=["folder"])
    count_stmt = select(sa_func.count()).where(ReportFormMapping.template_id == t.id)
    count = (await db.execute(count_stmt)).scalar() or 0
    return _serialize_template(t, count)


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
        .order_by(ReportFormMapping.sheet_name.asc().nullsfirst(), ReportFormMapping.sort_order, ReportFormMapping.id)
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
