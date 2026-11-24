import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class JobResponse(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    workspace_id: uuid.UUID
    owner_id: uuid.UUID
    status: str
    attempt_count: int
    max_attempts: int
    last_error: Optional[str] = None
    created_at: datetime
    finished_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
