import json

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.collect_script import CollectScript
from app.services.collect_parser import parse_legacy_zip, parse_powershell_json
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
    file: UploadFile = File(...),
    asset_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    filename = (file.filename or "").lower()

    if filename.endswith(".json"):
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(400, "JSON 파싱 실패: 파일 형식을 확인하세요")
        summary = await parse_powershell_json(data, asset_id, db)
    elif filename.endswith(".zip"):
        summary = await parse_legacy_zip(content, asset_id, db)
    else:
        raise HTTPException(400, "지원하지 않는 파일 형식입니다 (.json 또는 .zip)")

    return {"status": "saved", "asset_id": asset_id, "summary": summary}


@router.post("/parse-preview")
async def parse_preview(
    file: UploadFile = File(...),
    asset_id: int = Query(...),
):
    """파싱만 하고 저장하지 않음 — 미리보기용"""
    content = await file.read()
    filename = (file.filename or "").lower()

    if filename.endswith(".json"):
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(400, "JSON 파싱 실패")
        preview = {}
        for key, val in data.items():
            if key == "_meta":
                continue
            if isinstance(val, list):
                preview[key] = len(val)
            elif isinstance(val, dict):
                preview[key] = 1
        return {
            "status": "preview",
            "counts": preview,
            "meta": data.get("_meta", {}),
        }
    elif filename.endswith(".zip"):
        import io
        import zipfile

        try:
            with zipfile.ZipFile(io.BytesIO(content)) as zf:
                files = [n.split("/")[-1] for n in zf.namelist() if n.endswith(".txt")]
        except zipfile.BadZipFile:
            raise HTTPException(400, "ZIP 파일이 손상되었습니다")
        return {"status": "preview", "files": files, "file_count": len(files)}
    else:
        raise HTTPException(400, "지원하지 않는 파일 형식입니다 (.json 또는 .zip)")


@router.post("/confirm")
async def confirm_save(
    file: UploadFile = File(...),
    asset_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """미리보기 확인 후 실제 저장 — /upload와 동일 로직"""
    content = await file.read()
    filename = (file.filename or "").lower()

    if filename.endswith(".json"):
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(400, "JSON 파싱 실패")
        summary = await parse_powershell_json(data, asset_id, db)
    elif filename.endswith(".zip"):
        summary = await parse_legacy_zip(content, asset_id, db)
    else:
        raise HTTPException(400, "지원하지 않는 파일 형식입니다 (.json 또는 .zip)")

    return {"status": "saved", "asset_id": asset_id, "summary": summary}
