from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.master import Department, GroupNode, Person, PersonGroupRole
from app.schemas.master import (
    DepartmentCreate,
    DepartmentRead,
    DepartmentUpdate,
    PersonCreate,
    PersonRead,
    PersonUpdate,
)
from app.services.asset_manager_assignment import backfill_asset_managers_for_groups

router = APIRouter()
PRIMARY_ROLE = "PRIMARY"


def _serialize_person(row: Person) -> dict:
    return {
        "id": row.id,
        "name": row.name,
        "title": row.title,
        "contact": row.contact,
        "group_roles": [
            {
                "id": role.id,
                "group_id": role.group_id,
                "role_type": role.role_type,
                "group_name": role.group.name if role.group else None,
                "group_full_path": role.group.full_path if role.group else None,
            }
            for role in row.group_roles
        ],
    }


async def _load_person_payload(db: AsyncSession, person_id: int) -> dict:
    result = await db.execute(
        select(Person)
        .options(selectinload(Person.group_roles).selectinload(PersonGroupRole.group))
        .where(Person.id == person_id)
        .execution_options(populate_existing=True)
    )
    return _serialize_person(result.scalar_one())


async def _sync_person_group_roles(
    db: AsyncSession,
    person: Person,
    role_items: list[dict],
) -> None:
    await db.execute(delete(PersonGroupRole).where(PersonGroupRole.person_id == person.id))
    await db.flush()

    seen_group_ids: set[int] = set()
    for item in role_items:
        group = await db.get(GroupNode, item["group_id"])
        if not group:
            raise HTTPException(404, "그룹 정보를 찾을 수 없습니다")

        if item["group_id"] in seen_group_ids:
            raise HTTPException(400, "같은 그룹은 한 번만 지정할 수 있습니다")
        seen_group_ids.add(item["group_id"])

        db.add(
            PersonGroupRole(
                person_id=person.id,
                group_id=item["group_id"],
                role_type=PRIMARY_ROLE,
            )
        )

    await db.flush()


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
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    await db.flush()
    await db.refresh(row)
    return row


@router.delete("/departments/{dept_id}", status_code=204)
async def delete_department(dept_id: int, db: AsyncSession = Depends(get_db)):
    row = await db.get(Department, dept_id)
    if row:
        await db.delete(row)


@router.get("", response_model=list[PersonRead])
async def get_persons(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Person)
        .options(selectinload(Person.group_roles).selectinload(PersonGroupRole.group))
        .order_by(Person.id)
    )
    return [_serialize_person(row) for row in result.scalars().all()]


@router.post("", response_model=PersonRead, status_code=201)
async def create_person(body: PersonCreate, db: AsyncSession = Depends(get_db)):
    row = Person(**body.model_dump(exclude={"group_roles"}))
    db.add(row)
    await db.flush()
    group_role_items = [item.model_dump() for item in body.group_roles]
    await _sync_person_group_roles(db, row, group_role_items)
    await backfill_asset_managers_for_groups(db, [item["group_id"] for item in group_role_items])
    await db.flush()
    return await _load_person_payload(db, row.id)


@router.patch("/{person_id}", response_model=PersonRead)
async def update_person(person_id: int, body: PersonUpdate, db: AsyncSession = Depends(get_db)):
    row = await db.get(Person, person_id, options=[selectinload(Person.group_roles)])
    if not row:
        raise HTTPException(404, "담당자를 찾을 수 없습니다")

    data = body.model_dump(exclude_unset=True, exclude={"group_roles"})
    for key, value in data.items():
        setattr(row, key, value)

    if body.group_roles is not None:
        group_role_items = [item.model_dump() for item in body.group_roles]
        await _sync_person_group_roles(db, row, group_role_items)
        await backfill_asset_managers_for_groups(db, [item["group_id"] for item in group_role_items])

    await db.flush()
    return await _load_person_payload(db, row.id)


@router.delete("/{person_id}", status_code=204)
async def delete_person(person_id: int, db: AsyncSession = Depends(get_db)):
    row = await db.get(Person, person_id)
    if row:
        await db.delete(row)
