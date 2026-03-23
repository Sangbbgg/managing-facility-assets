from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.schemas.master import (
    DepartmentCreate, DepartmentRead, DepartmentUpdate,
    PersonCreate, PersonRead, PersonUpdate,
)
from app.models.master import Department, Person

router = APIRouter()


# ─── 부서 ────────────────────────────────────────────────────────────────────

@router.get("/departments", response_model=list[DepartmentRead])
async def get_departments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Department).order_by(Department.id))
    return result.scalars().all()


@router.post("/departments", response_model=DepartmentRead, status_code=201)
async def create_department(body: DepartmentCreate, db: AsyncSession = Depends(get_db)):
    row = Department(**body.model_dump())
    db.add(row)
    await db.flush()
    await db.refresh(row)
    return row


@router.patch("/departments/{dept_id}", response_model=DepartmentRead)
async def update_department(dept_id: int, body: DepartmentUpdate, db: AsyncSession = Depends(get_db)):
    row = await db.get(Department, dept_id)
    if not row:
        raise HTTPException(404, "부서를 찾을 수 없습니다")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    await db.flush()
    await db.refresh(row)
    return row


@router.delete("/departments/{dept_id}", status_code=204)
async def delete_department(dept_id: int, db: AsyncSession = Depends(get_db)):
    row = await db.get(Department, dept_id)
    if row:
        await db.delete(row)


# ─── 담당자 ──────────────────────────────────────────────────────────────────

@router.get("", response_model=list[PersonRead])
async def get_persons(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Person).order_by(Person.id))
    return result.scalars().all()


@router.post("", response_model=PersonRead, status_code=201)
async def create_person(body: PersonCreate, db: AsyncSession = Depends(get_db)):
    row = Person(**body.model_dump())
    db.add(row)
    await db.flush()
    await db.refresh(row)
    return row


@router.patch("/{person_id}", response_model=PersonRead)
async def update_person(person_id: int, body: PersonUpdate, db: AsyncSession = Depends(get_db)):
    row = await db.get(Person, person_id)
    if not row:
        raise HTTPException(404, "담당자를 찾을 수 없습니다")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    await db.flush()
    await db.refresh(row)
    return row


@router.delete("/{person_id}", status_code=204)
async def delete_person(person_id: int, db: AsyncSession = Depends(get_db)):
    row = await db.get(Person, person_id)
    if row:
        await db.delete(row)
