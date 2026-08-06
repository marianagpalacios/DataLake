from fastapi import APIRouter

from datalake.api.dependencies import SessionDep
from datalake.api.repositories.ingestion_runs import (
    get_staged_record_lineage,
)
from datalake.api.schemas import (
    DataQualityIssueRead,
    IngestionRunRead,
    PatientRead,
    SourceFileRead,
    StagedPatientRecordRead,
    StagedRecordLineageRead,
)


router = APIRouter(
    prefix="/staged-records",
    tags=["lineage"],
)


@router.get(
    "/{record_id}/lineage",
    response_model=StagedRecordLineageRead,
)
def read_record_lineage(
    record_id: int,
    session: SessionDep,
) -> StagedRecordLineageRead:
    record = get_staged_record_lineage(
        session,
        record_id,
    )

    patient = (
        PatientRead.model_validate(
            record.patient
        )
        if record.patient is not None
        else None
    )

    return StagedRecordLineageRead(
        record=(
            StagedPatientRecordRead
            .model_validate(record)
        ),
        ingestion_run=(
            IngestionRunRead.model_validate(
                record.ingestion_run
            )
        ),
        source_file=(
            SourceFileRead.model_validate(
                record.ingestion_run.source_file
            )
        ),
        patient=patient,
        issues=[
            DataQualityIssueRead.model_validate(
                issue
            )
            for issue in record.quality_issues
        ],
    )