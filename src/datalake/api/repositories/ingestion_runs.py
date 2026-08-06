from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import (
    Session,
    joinedload,
    selectinload,
)

from datalake.api.exceptions import (
    ResourceNotFoundError,
)
from datalake.models.data_quality_issue_record import (
    DataQualityIssueRecord,
)
from datalake.models.ingestion_run import IngestionRun
from datalake.models.staged_patient_record import (
    StagedPatientRecord,
)


def list_ingestion_runs(
    session: Session,
    *,
    offset: int,
    limit: int,
    status: str | None = None,
    source_file_id: int | None = None,
    started_from: datetime | None = None,
    started_to: datetime | None = None,
) -> tuple[list[IngestionRun], int]:
    conditions = []

    if status:
        conditions.append(
            IngestionRun.status == status
        )

    if source_file_id is not None:
        conditions.append(
            IngestionRun.source_file_id
            == source_file_id
        )

    if started_from is not None:
        conditions.append(
            IngestionRun.started_at
            >= started_from
        )

    if started_to is not None:
        conditions.append(
            IngestionRun.started_at
            <= started_to
        )

    count_statement = (
        select(func.count())
        .select_from(IngestionRun)
        .where(*conditions)
    )

    total = (
        session.scalar(count_statement)
        or 0
    )

    statement = (
        select(IngestionRun)
        .where(*conditions)
        .order_by(IngestionRun.id.desc())
        .offset(offset)
        .limit(limit)
    )

    runs = list(
        session.scalars(statement)
    )

    return runs, total


def get_ingestion_run(
    session: Session,
    run_uuid: UUID,
) -> IngestionRun:
    statement = select(
        IngestionRun
    ).where(
        IngestionRun.run_uuid == run_uuid
    )

    run = session.scalar(statement)

    if run is None:
        raise ResourceNotFoundError(
            "Execução de ingestão",
            run_uuid,
        )

    return run


def list_staged_records(
    session: Session,
    *,
    run_uuid: UUID,
    offset: int,
    limit: int,
    validation_status: str | None = None,
) -> tuple[list[StagedPatientRecord], int]:
    get_ingestion_run(
        session,
        run_uuid,
    )

    conditions = [
        IngestionRun.run_uuid == run_uuid,
    ]

    if validation_status:
        conditions.append(
            StagedPatientRecord.validation_status
            == validation_status
        )

    count_statement = (
        select(func.count())
        .select_from(StagedPatientRecord)
        .join(
            IngestionRun,
            IngestionRun.id
            == StagedPatientRecord.ingestion_run_id,
        )
        .where(*conditions)
    )

    total = (
        session.scalar(count_statement)
        or 0
    )

    statement = (
        select(StagedPatientRecord)
        .join(
            IngestionRun,
            IngestionRun.id
            == StagedPatientRecord.ingestion_run_id,
        )
        .where(*conditions)
        .order_by(
            StagedPatientRecord.source_row_number
        )
        .offset(offset)
        .limit(limit)
    )

    records = list(
        session.scalars(statement)
    )

    return records, total


def list_quality_issues(
    session: Session,
    *,
    run_uuid: UUID,
    offset: int,
    limit: int,
    field: str | None = None,
    code: str | None = None,
) -> tuple[
    list[DataQualityIssueRecord],
    int,
]:
    get_ingestion_run(
        session,
        run_uuid,
    )

    conditions = [
        IngestionRun.run_uuid == run_uuid,
    ]

    if field:
        conditions.append(
            DataQualityIssueRecord.field
            == field
        )

    if code:
        conditions.append(
            DataQualityIssueRecord.code
            == code
        )

    count_statement = (
        select(func.count())
        .select_from(DataQualityIssueRecord)
        .join(
            StagedPatientRecord,
            StagedPatientRecord.id
            == DataQualityIssueRecord.staged_record_id,
        )
        .join(
            IngestionRun,
            IngestionRun.id
            == StagedPatientRecord.ingestion_run_id,
        )
        .where(*conditions)
    )

    total = (
        session.scalar(count_statement)
        or 0
    )

    statement = (
        select(DataQualityIssueRecord)
        .join(
            StagedPatientRecord,
            StagedPatientRecord.id
            == DataQualityIssueRecord.staged_record_id,
        )
        .join(
            IngestionRun,
            IngestionRun.id
            == StagedPatientRecord.ingestion_run_id,
        )
        .where(*conditions)
        .order_by(
            DataQualityIssueRecord.id
        )
        .offset(offset)
        .limit(limit)
    )

    issues = list(
        session.scalars(statement)
    )

    return issues, total


def get_staged_record_lineage(
    session: Session,
    record_id: int,
) -> StagedPatientRecord:
    statement = (
        select(StagedPatientRecord)
        .options(
            joinedload(
                StagedPatientRecord.ingestion_run
            ).joinedload(
                IngestionRun.source_file
            ),
            joinedload(
                StagedPatientRecord.patient
            ),
            selectinload(
                StagedPatientRecord.quality_issues
            ),
        )
        .where(
            StagedPatientRecord.id
            == record_id
        )
    )

    record = session.scalar(statement)

    if record is None:
        raise ResourceNotFoundError(
            "Registro de staging",
            record_id,
        )

    return record