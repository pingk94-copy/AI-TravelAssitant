from datetime import datetime
from typing import Any

from pydantic import BaseModel


class TaskSubmitResponse(BaseModel):
    task_id: int
    status: str


class TaskResponse(BaseModel):
    id: int
    task_type: str
    status: str
    input: dict[str, Any]
    output: dict[str, Any] | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
