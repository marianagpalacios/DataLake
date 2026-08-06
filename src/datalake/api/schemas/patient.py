from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


BiologicalSex = Literal[
    "female",
    "male",
    "intersex",
    "unknown",
    "not_informed",
]


class PatientRead(BaseModel):
    """Representação pública de um paciente."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    external_code: str
    birth_date: date | None
    biological_sex: BiologicalSex | None
    created_at: datetime
    updated_at: datetime