from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from datalake.database.session import session_scope
from datalake.ingestion.mappers import map_patient_record
from datalake.ingestion.readers import read_csv_file
from datalake.ingestion.validators import validate_patient_dataframe
from datalake.models.data_quality_issue_record import (
    DataQualityIssueRecord,
)
from datalake.models.data_source import DataSource
from datalake.models.ingestion_run import IngestionRun
from datalake.models.patient import Patient
from datalake.models.source_file import SourceFile
from datalake.models.staged_patient_record import StagedPatientRecord
from datalake.pipeline.artifacts import (
    write_processed_patient_file,
)
from datalake.pipeline.exceptions import PatientETLError
from datalake.pipeline.files import prepare_source_file
from datalake.quality.reports import (
    write_rejected_patient_report,
)


SUCCESSFUL_STATUSES = (
    "completed",
    "completed_with_rejections",
)


@dataclass(frozen=True)
class PatientETLResult:
    run_uuid: UUID
    status: str
    source_file: Path
    source_sha256: str
    raw_file: Path
    processed_file: Path | None
    rejection_file: Path | None
    received_count: int
    valid_count: int
    rejected_count: int
    inserted_count: int
    existing_count: int
    acceptance_rate: float
    warnings: tuple[str, ...]
    duplicate_of_run_uuid: UUID | None


def _get_or_create_data_source(
    session,
    source_name: str,
) -> DataSource:
    source = session.scalar(
        select(DataSource).where(
            DataSource.name == source_name
        )
    )

    if source is None:
        source = DataSource(
            name=source_name,
            source_type="csv",
            description=(
                "Fonte registrada automaticamente "
                "pelo pipeline de pacientes."
            ),
        )

        session.add(source)
        session.flush()

    elif source.source_type != "csv":
        raise PatientETLError(
            "A fonte informada já existe com um tipo "
            "diferente de CSV."
        )

    return source


def _mark_run_failed(
    run_id: int,
    error: Exception,
) -> None:
    try:
        with session_scope() as session:
            run = session.get(
                IngestionRun,
                run_id,
            )

            if run is None:
                return

            run.status = "failed"
            run.finished_at = datetime.now(
                timezone.utc
            )
            run.error_message = str(error)[:2000]

    except SQLAlchemyError:
        # A falha original deve continuar sendo a principal.
        pass


def run_patient_etl(
    file_path: str | Path,
    source_name: str = "patient_csv_cli",
    raw_dir: str | Path = "data/raw",
    processed_dir: str | Path = "data/processed",
    rejected_dir: str | Path = "data/rejected",
    force: bool = False,
) -> PatientETLResult:
    prepared = prepare_source_file(
        file_path=file_path,
        raw_dir=raw_dir,
    )

    run_id: int | None = None
    run_uuid: UUID | None = None

    with session_scope() as session:
        data_source = _get_or_create_data_source(
            session,
            source_name,
        )

        source_file = session.scalar(
            select(SourceFile).where(
                SourceFile.data_source_id
                == data_source.id,
                SourceFile.sha256
                == prepared.sha256,
            )
        )

        if source_file is None:
            source_file = SourceFile(
                data_source_id=data_source.id,
                sha256=prepared.sha256,
                original_name=(
                    prepared.original_path.name
                ),
                stored_path=str(prepared.raw_path),
                size_bytes=prepared.size_bytes,
            )

            session.add(source_file)
            session.flush()

        previous_run = session.scalar(
            select(IngestionRun)
            .where(
                IngestionRun.source_file_id
                == source_file.id,
                IngestionRun.status.in_(
                    SUCCESSFUL_STATUSES
                ),
            )
            .order_by(
                IngestionRun.finished_at.desc(),
                IngestionRun.id.desc(),
            )
            .limit(1)
        )

        if previous_run is not None and not force:
            skipped_run = IngestionRun(
                source_file_id=source_file.id,
                duplicate_of_run_id=previous_run.id,
                status="skipped_duplicate",
                pipeline_version="0.5.0",
                finished_at=datetime.now(timezone.utc),
                received_count=previous_run.received_count,
                valid_count=previous_run.valid_count,
                rejected_count=(
                    previous_run.rejected_count
                ),
                inserted_count=previous_run.inserted_count,
                existing_count=previous_run.existing_count,
                acceptance_rate=previous_run.acceptance_rate,
                processed_file_path=(
                    previous_run.processed_file_path
                ),
                rejection_file_path=(
                    previous_run.rejection_file_path
                ),
            )

            session.add(skipped_run)
            session.flush()

            return PatientETLResult(
                run_uuid=skipped_run.run_uuid,
                status=skipped_run.status,
                source_file=prepared.original_path,
                source_sha256=prepared.sha256,
                raw_file=prepared.raw_path,
                processed_file=(
                    Path(previous_run.processed_file_path)
                    if previous_run.processed_file_path
                    else None
                ),
                rejection_file=(
                    Path(previous_run.rejection_file_path)
                    if previous_run.rejection_file_path
                    else None
                ),
                received_count=skipped_run.received_count,
                valid_count=skipped_run.valid_count,
                rejected_count=skipped_run.rejected_count,
                inserted_count=0,
                existing_count=skipped_run.valid_count,
                acceptance_rate=float(
                    skipped_run.acceptance_rate
                ),
                warnings=(
                    "O arquivo já havia sido processado "
                    "com sucesso e foi ignorado.",
                ),
                duplicate_of_run_uuid=(
                    previous_run.run_uuid
                ),
            )

        run = IngestionRun(
            source_file_id=source_file.id,
            status="running",
            pipeline_version="0.5.0",
        )

        session.add(run)
        session.flush()

        run_id = run.id
        run_uuid = run.run_uuid

    assert run_id is not None
    assert run_uuid is not None

    try:
        dataframe = read_csv_file(
            prepared.raw_path
        )

        validation = validate_patient_dataframe(
            dataframe
        )

        processed_file = write_processed_patient_file(
            valid_records=validation.valid_records,
            source_file=prepared.original_path,
            run_uuid=run_uuid,
            output_dir=processed_dir,
        )

        rejection_file = (
            write_rejected_patient_report(
                rejected_records=(
                    validation.rejected_records
                ),
                source_file=prepared.original_path,
                output_dir=rejected_dir,
            )
        )

        with session_scope() as session:
            run = session.get(
                IngestionRun,
                run_id,
            )

            if run is None:
                raise PatientETLError(
                    "A execução registrada não foi encontrada."
                )

            external_codes = [
                str(
                    validated.normalized_record[
                        "external_code"
                    ]
                )
                for validated in validation.valid_records
            ]

            existing_patients: list[Patient] = []

            if external_codes:
                existing_patients = list(
                    session.scalars(
                        select(Patient).where(
                            Patient.external_code.in_(
                                external_codes
                            )
                        )
                    )
                )

            patients_by_code = {
                patient.external_code: patient
                for patient in existing_patients
            }

            inserted_count = 0

            for validated in validation.valid_records:
                code = str(
                    validated.normalized_record[
                        "external_code"
                    ]
                )

                if code in patients_by_code:
                    continue

                patient = map_patient_record(
                    validated.normalized_record
                )

                session.add(patient)
                patients_by_code[code] = patient
                inserted_count += 1

            session.flush()

            for validated in validation.valid_records:
                normalized = validated.normalized_record
                code = str(normalized["external_code"])

                session.add(
                    StagedPatientRecord(
                        ingestion_run_id=run.id,
                        source_row_number=(
                            validated.row_number
                        ),
                        raw_record=dict(
                            validated.raw_record
                        ),
                        normalized_external_code=code,
                        normalized_birth_date=(
                            normalized.get("birth_date")
                        ),
                        normalized_biological_sex=(
                            normalized.get(
                                "biological_sex"
                            )
                        ),
                        validation_status="valid",
                        patient_id=(
                            patients_by_code[code].id
                        ),
                    )
                )

            rejected_pairs: list[
                tuple[object, StagedPatientRecord]
            ] = []

            for rejected in validation.rejected_records:
                staged = StagedPatientRecord(
                    ingestion_run_id=run.id,
                    source_row_number=(
                        rejected.row_number
                    ),
                    raw_record=dict(
                        rejected.raw_record
                    ),
                    validation_status="rejected",
                )

                session.add(staged)
                rejected_pairs.append((rejected, staged))

            session.flush()

            for rejected, staged in rejected_pairs:
                for issue in rejected.issues:
                    session.add(
                        DataQualityIssueRecord(
                            staged_record_id=staged.id,
                            field=issue.field,
                            code=issue.code,
                            message=issue.message,
                            raw_value=issue.raw_value,
                        )
                    )

            existing_count = len(existing_patients)

            run.status = (
                "completed_with_rejections"
                if validation.rejected_count
                else "completed"
            )
            run.finished_at = datetime.now(timezone.utc)
            run.received_count = validation.received_count
            run.valid_count = validation.valid_count
            run.rejected_count = validation.rejected_count
            run.inserted_count = inserted_count
            run.existing_count = existing_count
            run.acceptance_rate = Decimal(
                str(validation.acceptance_rate)
            )
            run.processed_file_path = (
                str(processed_file)
                if processed_file is not None
                else None
            )
            run.rejection_file_path = (
                str(rejection_file)
                if rejection_file is not None
                else None
            )

        return PatientETLResult(
            run_uuid=run_uuid,
            status=run.status,
            source_file=prepared.original_path,
            source_sha256=prepared.sha256,
            raw_file=prepared.raw_path,
            processed_file=processed_file,
            rejection_file=rejection_file,
            received_count=validation.received_count,
            valid_count=validation.valid_count,
            rejected_count=validation.rejected_count,
            inserted_count=inserted_count,
            existing_count=existing_count,
            acceptance_rate=validation.acceptance_rate,
            warnings=validation.warnings,
            duplicate_of_run_uuid=None,
        )

    except Exception as error:
        _mark_run_failed(
            run_id,
            error,
        )

        if isinstance(error, PatientETLError):
            raise

        raise PatientETLError(
            "O pipeline ETL de pacientes falhou."
        ) from error
