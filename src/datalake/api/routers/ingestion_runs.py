from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from datalake.api.dependencies import (
    PaginationDep,
    SessionDep,
)
from datalake.api.pagination import (
    Page,
    build_page,
)
from datalake.api.repositories.ingestion_runs import (
    get_ingestion_run,
    list_ingestion_runs,
    list_quality_issues,
    list_staged_records,
)
from datalake.api.schemas import (
    DataQualityIssueRead,
    IngestionRunRead,
    IngestionRunStatus,
    StagedPatientRecordRead,
    ValidationStatus,
)


router = APIRouter(
    prefix="/ingestion-runs",
    tags=["ingestion-runs"],
)


@router.get(
    "",
    response_model=Page[IngestionRunRead],
)
def read_ingestion_runs(
    session: SessionDep,
    pagination: PaginationDep,
    status: IngestionRunStatus | None = None,
    source_file_id: int | None = None,
    started_from: datetime | None = None,
    started_to: datetime | None = None,
) -> Page[IngestionRunRead]:
    runs, total = list_ingestion_runs(
        session,
        offset=pagination.offset,
        limit=pagination.size,
        status=status,
        source_file_id=source_file_id,
        started_from=started_from,
        started_to=started_to,
    )

    items = [
        IngestionRunRead.model_validate(run)
        for run in runs
    ]

    return build_page(
        items,
        total=total,
        page=pagination.page,
        size=pagination.size,
    )


@router.get(
    "/{run_uuid}",
    response_model=IngestionRunRead,
)
def read_ingestion_run(
    run_uuid: UUID,
    session: SessionDep,
) -> IngestionRunRead:
    run = get_ingestion_run(
        session,
        run_uuid,
    )

    return IngestionRunRead.model_validate(
        run
    )


@router.get(
    "/{run_uuid}/records",
    response_model=Page[
        StagedPatientRecordRead
    ],
)
def read_run_records(
    run_uuid: UUID,
    session: SessionDep,
    pagination: PaginationDep,
    validation_status: ValidationStatus
    | None = None,
) -> Page[StagedPatientRecordRead]:
    records, total = list_staged_records(
        session,
        run_uuid=run_uuid,
        offset=pagination.offset,
        limit=pagination.size,
        validation_status=validation_status,
    )

    items = [
        StagedPatientRecordRead.model_validate(
            record
        )
        for record in records
    ]

    return build_page(
        items,
        total=total,
        page=pagination.page,
        size=pagination.size,
    )


@router.get(
    "/{run_uuid}/quality-issues",
    response_model=Page[
        DataQualityIssueRead
    ],
)
def read_run_quality_issues(
    run_uuid: UUID,
    session: SessionDep,
    pagination: PaginationDep,
    field: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=100,
        ),
    ] = None,
    code: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=100,
        ),
    ] = None,
) -> Page[DataQualityIssueRead]:
    issues, total = list_quality_issues(
        session,
        run_uuid=run_uuid,
        offset=pagination.offset,
        limit=pagination.size,
        field=field,
        code=code,
    )

    items = [
        DataQualityIssueRead.model_validate(
            issue
        )
        for issue in issues
    ]

    return build_page(
        items,
        total=total,
        page=pagination.page,
        size=pagination.size,
    )