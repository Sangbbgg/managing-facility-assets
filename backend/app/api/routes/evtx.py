from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from pathlib import Path
import shutil
import uuid
from app.core.database import get_db
from app.services.evtx_parser import parse_evtx_directory

router = APIRouter()
UPLOAD_DIR = Path("/app/data/evtx_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_evtx(
    files: list[UploadFile] = File(...),
    asset_id: int = Form(...),
    record_date: date = Form(...),
    db: AsyncSession = Depends(get_db),
):
    job_dir = UPLOAD_DIR / str(uuid.uuid4())
    job_dir.mkdir()
    for f in files:
        with open(job_dir / f.filename, "wb") as out:
            shutil.copyfileobj(f.file, out)

    count = await parse_evtx_directory(job_dir, asset_id, record_date, db)
    shutil.rmtree(job_dir)
    return {"parsed_event_types": count, "asset_id": asset_id, "record_date": str(record_date)}
