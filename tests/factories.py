from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Session

from datalake.models.data_quality_issue_record import (
    DataQualityIssueRecord,
)
from datalake.models.data_source import DataSource
from datalake.models.ingestion_run import IngestionRun
from datalake.models.patient import Patient
from datalake.models.source_file import SourceFile
from datalake.models.staged_patient_record import (
    StagedPatientRecord,
)


def create_patient(
    session: Session,
    *,
    external_code: str | None = None,
    biological_sex: str | None = "unknown",
) -> Patient:
    patient = Patient(
        external_code=(
            external_code
            or f"TEST-{uuid4().hex[:12].upper()}"
        ),
        biological_sex=biological_sex,
    )

    session.add(patient)
    session.flush()

    return patient


def create_data_source(
    session: Session,
    *,
    name: str | None = None,
) -> DataSource:
    source = DataSource(
        name=(
            name
            or f"test-source-{uuid4().hex}"
        ),
        source_type="csv",
        description="Fonte sintética de teste.",
    )

    session.add(source)
    session.flush()

    return source


def create_source_file(
    session: Session,
    *,
    data_source: DataSource,
    sha256: str | None = None,
) -> SourceFile:
    file_hash = (
        sha256
        or uuid4().hex * 2
    )

    source_file = SourceFile(
        data_source_id=data_source.id,
        sha256=file_hash,
        original_name="patients.csv",
        stored_path="data/raw/patients.csv",
        size_bytes=128,
    )

    session.add(source_file)
    session.flush()

    return source_file


def create_ingestion_run(
    session: Session,
    *,
    source_file: SourceFile,
    status: str = "completed",
    received_count: int = 1,
    valid_count: int = 1,
    rejected_count: int = 0,
    inserted_count: int = 1,
    existing_count: int = 0,
) -> IngestionRun:
    run = IngestionRun(
        source_file_id=source_file.id,
        status=status,
        pipeline_version="0.5.0",
        finished_at=datetime.now(
            timezone.utc
        ),
        received_count=received_count,
        valid_count=valid_count,
        rejected_count=rejected_count,
        inserted_count=inserted_count,
        existing_count=existing_count,
        acceptance_rate=Decimal(
            str(
                valid_count
                / received_count
                * 100
                if received_count
                else 0
            )
        ),
    )

    session.add(run)
    session.flush()

    return run


def create_staged_record(
    session: Session,
    *,
    run: IngestionRun,
    patient: Patient | None = None,
    validation_status: str = "valid",
) -> StagedPatientRecord:
    record = StagedPatientRecord(
        ingestion_run_id=run.id,
        source_row_number=2,
        raw_record={
            "external_code": (
                patient.external_code
                if patient
                else "INVALID"
            ),
        },
        normalized_external_code=(
            patient.external_code
            if patient
            else None
        ),
        validation_status=validation_status,
        patient_id=(
            patient.id
            if patient
            else None
        ),
    )

    session.add(record)
    session.flush()

    return record


def create_quality_issue(
    session: Session,
    *,
    staged_record: StagedPatientRecord,
    code: str = "invalid_date_format",
) -> DataQualityIssueRecord:
    issue = DataQualityIssueRecord(
        staged_record_id=staged_record.id,
        field="birth_date",
        code=code,
        message=(
            "A data deve usar o formato "
            "AAAA-MM-DD."
        ),
        raw_value="10/04/1995",
    )

    session.add(issue)
    session.flush()

    return issue