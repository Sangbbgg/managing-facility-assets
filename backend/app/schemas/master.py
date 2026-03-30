from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel


class LocationNodeBase(BaseModel):
    name: str
    parent_id: Optional[int] = None


class LocationNodeCreate(LocationNodeBase):
    pass


class LocationNodeUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None


class LocationNodeRead(LocationNodeBase):
    id: int
    full_path: str
    depth: int

    model_config = {"from_attributes": True}


class GroupNodeBase(BaseModel):
    name: str
    parent_id: Optional[int] = None
    code: Optional[str] = None
    display_code: Optional[str] = None


class GroupNodeCreate(GroupNodeBase):
    pass


class GroupNodeUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    code: Optional[str] = None
    display_code: Optional[str] = None


class GroupNodeRead(GroupNodeBase):
    id: int
    full_path: str
    depth: int

    model_config = {"from_attributes": True}


class EquipmentTypeBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None


class EquipmentTypeCreate(EquipmentTypeBase):
    pass


class EquipmentTypeUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None


class EquipmentTypeRead(EquipmentTypeBase):
    id: int

    model_config = {"from_attributes": True}


class OsCatalogBase(BaseModel):
    name: str
    version: Optional[str] = None
    eol_date: Optional[date] = None
    extended_eol: Optional[date] = None
    notes: Optional[str] = None


class OsCatalogCreate(OsCatalogBase):
    pass


class OsCatalogUpdate(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    eol_date: Optional[date] = None
    extended_eol: Optional[date] = None
    notes: Optional[str] = None


class OsCatalogRead(OsCatalogBase):
    id: int

    model_config = {"from_attributes": True}


class AntivirusCatalogBase(BaseModel):
    name: str
    version: Optional[str] = None
    support_end: Optional[date] = None
    notes: Optional[str] = None


class AntivirusCatalogCreate(AntivirusCatalogBase):
    pass


class AntivirusCatalogUpdate(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    support_end: Optional[date] = None
    notes: Optional[str] = None


class AntivirusCatalogRead(AntivirusCatalogBase):
    id: int

    model_config = {"from_attributes": True}


class DepartmentBase(BaseModel):
    name: str
    code: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None


class DepartmentRead(DepartmentBase):
    id: int

    model_config = {"from_attributes": True}


class PersonBase(BaseModel):
    name: str
    title: Optional[str] = None
    contact: Optional[str] = None
    dept_id: Optional[int] = None


class PersonGroupRoleBase(BaseModel):
    group_id: int
    role_type: Literal["PRIMARY"]


class PersonGroupRoleCreate(PersonGroupRoleBase):
    pass


class PersonGroupRoleRead(PersonGroupRoleBase):
    id: int
    group_name: Optional[str] = None
    group_full_path: Optional[str] = None


class PersonCreate(PersonBase):
    group_roles: list[PersonGroupRoleCreate] = []


class PersonUpdate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    contact: Optional[str] = None
    dept_id: Optional[int] = None
    group_roles: Optional[list[PersonGroupRoleCreate]] = None


class PersonRead(PersonBase):
    id: int
    department_name: Optional[str] = None
    group_roles: list[PersonGroupRoleRead] = []

    model_config = {"from_attributes": True}
