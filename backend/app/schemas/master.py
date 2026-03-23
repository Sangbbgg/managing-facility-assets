from pydantic import BaseModel
from typing import Optional
from datetime import date


# ── LocationNode ──────────────────────────────────────────────
class LocationNodeBase(BaseModel):
    name: str
    parent_id: Optional[int] = None

class LocationNodeCreate(LocationNodeBase):
    pass

class LocationNodeUpdate(BaseModel):
    name: Optional[str] = None

class LocationNodeRead(LocationNodeBase):
    id: int
    full_path: str
    depth: int
    model_config = {"from_attributes": True}


# ── GroupNode ─────────────────────────────────────────────────
class GroupNodeBase(BaseModel):
    name: str
    parent_id: Optional[int] = None
    code: Optional[str] = None

class GroupNodeCreate(GroupNodeBase):
    pass

class GroupNodeUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None

class GroupNodeRead(GroupNodeBase):
    id: int
    full_path: str
    depth: int
    model_config = {"from_attributes": True}


# ── EquipmentType ─────────────────────────────────────────────
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


# ── OsCatalog ─────────────────────────────────────────────────
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


# ── AntivirusCatalog ──────────────────────────────────────────
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


# ── Department ────────────────────────────────────────────────
class DepartmentBase(BaseModel):
    name: str
    code: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentRead(DepartmentBase):
    id: int
    model_config = {"from_attributes": True}


# ── Person ────────────────────────────────────────────────────
class PersonBase(BaseModel):
    name: str
    dept_id: Optional[int] = None
    title: Optional[str] = None
    contact: Optional[str] = None

class PersonCreate(PersonBase):
    pass

class PersonUpdate(BaseModel):
    name: Optional[str] = None
    dept_id: Optional[int] = None
    title: Optional[str] = None
    contact: Optional[str] = None

class PersonRead(PersonBase):
    id: int
    model_config = {"from_attributes": True}
