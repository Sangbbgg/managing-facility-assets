from fastapi import APIRouter

router = APIRouter()


@router.post("/upload")
async def upload_evtx():
    return {"message": "Phase 6에서 구현 예정"}
