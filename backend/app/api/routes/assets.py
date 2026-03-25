from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.config import settings
from app.schemas.asset import AssetCreate, AssetRead, AssetUpdate
from app.models.asset import Asset, AssetCodeSequence, AssetChangeLog
from app.models.master import GroupNode, EquipmentType
from app.services.asset_code import issue_asset_code

router = APIRouter()


# ─── 정적 경로 (파라미터 경로보다 먼저 등록해야 함) ─────────────────────────────

@router.get("/preview-code")
async def preview_asset_code(
    group_id: int = Query(...),
    type_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """채번하지 않고 다음 자산코드만 예측 반환"""
    group = await db.get(GroupNode, group_id)
    etype = await db.get(EquipmentType, type_id)
    if not group or not group.code:
        raise HTTPException(400, "code가 있는 그룹 노드를 선택해주세요")
    if not etype:
        raise HTTPException(400, "존재하지 않는 장비 종류입니다")

    seq_row = await db.scalar(
        select(AssetCodeSequence).where(
            AssetCodeSequence.group_code == group.code,
            AssetCodeSequence.type_code == etype.code,
        )
    )
    next_seq = (seq_row.last_seq + 1) if seq_row else 1
    preview = f"{settings.ASSET_PREFIX}-{group.code}-{etype.code}-{next_seq:04d}"
    return {
        "preview_code": preview,
        "group_code": group.code,
        "type_code": etype.code,
        "next_seq": next_seq,
    }


@router.get("/bulk-template")
async def download_bulk_template(db: AsyncSession = Depends(get_db)):
    """대량 등록용 엑셀 템플릿 다운로드 (드롭다운 + 자산코드 참고 포함)"""
    from app.services.bulk_register import generate_template
    file_path = await generate_template(db)
    return FileResponse(
        path=file_path,
        filename="자산_대량등록_템플릿.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.post("/bulk-register")
async def bulk_register(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """엑셀 파일 일괄 업로드 → 자산 대량 등록"""
    from app.services.bulk_register import parse_and_register
    result = await parse_and_register(file, db)
    return result


@router.get("/enriched")
async def get_enriched_assets(db: AsyncSession = Depends(get_db)):
    """자산 목록 + 모든 조인 데이터 (그룹/위치/OS/백신/담당자 등) 반환"""
    from app.services.report_builder.data_fetchers import fetch_asset_rows
    return await fetch_asset_rows(0, None, db)


# ─── 컬렉션 경로 ────────────────────────────────────────────────────────────────

@router.get("", response_model=list[AssetRead])
async def get_assets(
    group_id: int | None = Query(None),
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Asset).where(Asset.is_deleted == False)
    if group_id:
        stmt = stmt.where(Asset.group_id == group_id)
    if status:
        stmt = stmt.where(Asset.status == status)
    result = await db.execute(stmt.order_by(Asset.id))
    return result.scalars().all()


@router.post("", response_model=AssetRead, status_code=201)
async def create_asset(body: AssetCreate, db: AsyncSession = Depends(get_db)):
    group = await db.get(GroupNode, body.group_id)
    if not group or not group.code:
        raise HTTPException(400, "code가 있는 그룹 노드만 자산 등록 가능합니다")
    eq_type = await db.get(EquipmentType, body.equipment_type_id)
    if not eq_type:
        raise HTTPException(400, "존재하지 않는 장비 종류입니다")
    asset_code = await issue_asset_code(db, group.code, eq_type.code)
    asset = Asset(**body.model_dump(), asset_code=asset_code, is_deleted=False)
    db.add(asset)
    await db.flush()
    await db.refresh(asset)
    return asset


# ─── 단건 경로 (asset_id 파라미터) ──────────────────────────────────────────────

@router.get("/{asset_id}", response_model=AssetRead)
async def get_asset(asset_id: int, db: AsyncSession = Depends(get_db)):
    asset = await db.get(Asset, asset_id)
    if not asset or asset.is_deleted:
        raise HTTPException(404, "자산을 찾을 수 없습니다")
    return asset


@router.patch("/{asset_id}", response_model=AssetRead)
async def update_asset(asset_id: int, body: AssetUpdate, db: AsyncSession = Depends(get_db)):
    asset = await db.get(Asset, asset_id)
    if not asset or asset.is_deleted:
        raise HTTPException(404, "자산을 찾을 수 없습니다")

    # 변경 전 스냅샷 (변경 이력 기록)
    old_data = {k: getattr(asset, k) for k in body.model_dump(exclude_unset=True)}
    new_data = body.model_dump(exclude_unset=True)

    for k, v in new_data.items():
        setattr(asset, k, v)
    await db.flush()

    # 변경 이력 기록
    from app.services.change_logger import log_changes
    await log_changes(
        db=db, asset_id=asset_id,
        changed_by="system",
        old_data={k: str(v) if v is not None else None for k, v in old_data.items()},
        new_data={k: str(v) if v is not None else None for k, v in new_data.items()},
    )

    await db.refresh(asset)
    return asset


@router.delete("/{asset_id}", status_code=204)
async def delete_asset(asset_id: int, db: AsyncSession = Depends(get_db)):
    asset = await db.get(Asset, asset_id)
    if not asset or asset.is_deleted:
        raise HTTPException(404, "자산을 찾을 수 없습니다")
    asset.is_deleted = True


@router.get("/{asset_id}/change-log")
async def get_change_log(asset_id: int, db: AsyncSession = Depends(get_db)):
    """자산 변경 이력 조회"""
    result = await db.execute(
        select(AssetChangeLog)
        .where(AssetChangeLog.asset_id == asset_id)
        .order_by(AssetChangeLog.changed_at.desc())
    )
    return result.scalars().all()
