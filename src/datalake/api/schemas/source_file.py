from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SourceFileRead(BaseModel):
    """Metadados públicos de um arquivo recebido."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    data_source_id: int
    sha256: str
    original_name: str
    size_bytes: int
    created_at: datetime
    updated_at: datetime
