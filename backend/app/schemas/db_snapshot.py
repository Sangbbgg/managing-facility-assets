from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DatabaseSnapshotCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=2000)


class DatabaseSnapshotRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    snapshot_type: str
    restored_from_snapshot_id: Optional[int] = None
    table_count: int
    row_count: int
    table_counts_json: list[dict]
    created_at: datetime

    model_config = {"from_attributes": True}


class DatabaseSnapshotRestoreResult(BaseModel):
    message: str
    rollback_snapshot: Optional[DatabaseSnapshotRead] = None
