from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from datalake.api.schemas.ingestion_run import (
    IngestionRunRead,
)
from datalake.api.schemas.patient import PatientRead
from datalake.api.schemas.source_file import (
    SourceFileRead,
)


ValidationStatus = Literal[
    "valid",
    "rejected",
]


class StagedPatientRecordRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    ingestion_run_id: int
    source_row_number: int
    normalized_external_code: str | None
    normalized_birth_date: date | None
    normalized_biological_sex: str | None
    validation_status: ValidationStatus
    patient_id: int | None
    created_at: datetime


class DataQualityIssueRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    staged_record_id: int
    field: str
    code: str
    message: str
    created_at: datetime


class StagedRecordLineageRead(BaseModel):
    record: StagedPatientRecordRead
    ingestion_run: IngestionRunRead
    source_file: SourceFileRead
    patient: PatientRead | None
    issues: list[DataQualityIssueRead]