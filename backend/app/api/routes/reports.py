from fastapi import APIRouter

router = APIRouter()


@router.post("/generate")
async def generate_report():
    return {"message": "Phase 6에서 구현 예정"}
