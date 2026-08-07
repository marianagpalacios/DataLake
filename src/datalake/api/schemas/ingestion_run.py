from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

IngestionRunStatus = Literal[
    "running",
    "completed",
    "completed_with_rejections",
    "failed",
    "skipped_duplicate",
]


class IngestionRunRead(BaseModel):
    """Resumo público de uma execução."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    run_uuid: UUID
    source_file_id: int
    duplicate_of_run_id: int | None
    status: IngestionRunStatus
    pipeline_name: str
    pipeline_version: str
    started_at: datetime
    finished_at: datetime | None
    received_count: int
    valid_count: int
    rejected_count: int
    inserted_count: int
    existing_count: int
    acceptance_rate: float
    created_at: datetime
    updated_at: datetime
