import json

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.collect_script import CollectScript
from app.services.collect_parser import (
    build_collect_preview,
    parse_legacy_folder,
    parse_legacy_zip,
    parse_powershell_json,
    preview_legacy_folder,
    preview_legacy_zip,
)
from app.services.script_generator import generate_bundle_script, generate_single_script

router = APIRouter()


@router.get("/scripts")
async def get_collect_scripts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CollectScript)
        .where(CollectScript.is_active == True)
        .order_by(CollectScript.sort_order)
    )
    return result.scalars().all()


@router.get("/scripts/{key}/download")
async def download_single_script(key: str, db: AsyncSession = Depends(get_db)):
    try:
        file_path = await generate_single_script(db, key)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return FileResponse(
        path=file_path,
        filename=f"collect_{key}.ps1",
        media_type="text/plain; charset=utf-8",
    )


@router.get("/script-bundle")
async def download_bundle_script(db: AsyncSession = Depends(get_db)):
    file_path = await generate_bundle_script(db)
    return FileResponse(
        path=file_path,
        filename="collect_asset.ps1",
        media_type="text/plain; charset=utf-8",
    )


@router.patch("/scripts/{key}")
async def update_script(key: str, body: dict, db: AsyncSession = Depends(get_db)):
    script = await db.scalar(
        select(CollectScript).where(CollectScript.script_key == key)
    )
    if not script:
        raise HTTPException(404, "스크립트를 찾을 수 없습니다")
    allowed = {"display_name", "description", "ps_command", "is_active", "sort_order"}
    for k, v in body.items():
        if k in allowed:
            setattr(script, k, v)
    await db.flush()
    await db.refresh(script)
    return script


@router.post("/upload")
async def upload_collect_data(
    file: UploadFile | None = File(None),
    files: list[UploadFile] = File(default=[]),
    asset_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    summary = await _save_collect_upload(file, files, asset_id, db)

    return {"status": "saved", "asset_id": asset_id, "summary": summary}


@router.post("/parse-preview")
async def parse_preview(
    file: UploadFile | None = File(None),
    files: list[UploadFile] = File(default=[]),
    asset_id: int = Query(...),
):
    """파싱만 하고 저장하지 않음 — 미리보기용"""
    return await _preview_collect_upload(file, files)


@router.post("/confirm")
async def confirm_save(
    file: UploadFile | None = File(None),
    files: list[UploadFile] = File(default=[]),
    asset_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """미리보기 확인 후 실제 저장 — /upload와 동일 로직"""
    summary = await _save_collect_upload(file, files, asset_id, db)

    return {"status": "saved", "asset_id": asset_id, "summary": summary}


async def _preview_collect_upload(
    file: UploadFile | None,
    files: list[UploadFile],
):
    upload_kind, payload = await _resolve_collect_payload(file, files)

    if upload_kind == "json":
        try:
            data = json.loads(payload["content"])
        except json.JSONDecodeError:
            raise HTTPException(400, "JSON 파싱 실패")
        preview = build_collect_preview(data)
        preview["source_kind"] = "json"
        return preview

    if upload_kind == "zip":
        return preview_legacy_zip(payload["content"])

    if upload_kind == "folder":
        try:
            return preview_legacy_folder(payload["entries"])
        except ValueError as error:
            raise HTTPException(400, str(error))

    raise HTTPException(400, "지원하지 않는 업로드 형식입니다")


async def _save_collect_upload(
    file: UploadFile | None,
    files: list[UploadFile],
    asset_id: int,
    db: AsyncSession,
):
    upload_kind, payload = await _resolve_collect_payload(file, files)

    if upload_kind == "json":
        try:
            data = json.loads(payload["content"])
        except json.JSONDecodeError:
            raise HTTPException(400, "JSON 파싱 실패")
        return await parse_powershell_json(data, asset_id, db)

    if upload_kind == "zip":
        return await parse_legacy_zip(payload["content"], asset_id, db)

    if upload_kind == "folder":
        try:
            return await parse_legacy_folder(payload["entries"], asset_id, db)
        except ValueError as error:
            raise HTTPException(400, str(error))

    raise HTTPException(400, "지원하지 않는 업로드 형식입니다")


async def _resolve_collect_payload(
    file: UploadFile | None,
    files: list[UploadFile],
) -> tuple[str, dict]:
    folder_files = [item for item in files if item and item.filename]
    if folder_files:
        entries = [(item.filename or "", await item.read()) for item in folder_files]
        return "folder", {"entries": entries}

    if not file:
        raise HTTPException(400, "업로드할 파일 또는 폴더를 선택해 주세요")

    content = await file.read()
    filename = (file.filename or "").lower()
    if filename.endswith(".json"):
        return "json", {"content": content, "filename": filename}
    if filename.endswith(".zip"):
        return "zip", {"content": content, "filename": filename}
    raise HTTPException(400, "지원하지 않는 파일 형식입니다 (.json 또는 .zip)")
