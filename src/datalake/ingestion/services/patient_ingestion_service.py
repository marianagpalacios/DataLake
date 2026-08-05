from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from datalake.database.session import (
    session_scope,
)
from datalake.ingestion.exceptions import (
    PatientIngestionError,
)
from datalake.ingestion.mappers import (
    map_patient_record,
)
from datalake.ingestion.readers import (
    read_csv_file,
)
from datalake.ingestion.validators import (
    validate_patient_dataframe,
)
from datalake.models.patient import Patient
from datalake.quality.reports import (
    write_rejected_patient_report,
)


@dataclass(frozen=True)
class PatientIngestionResult:
    """Resumo de uma ingestão de pacientes."""

    source_file: Path
    received_count: int
    valid_count: int
    rejected_count: int
    inserted_count: int
    existing_count: int
    acceptance_rate: float
    warnings: tuple[str, ...]
    rejection_file: Path | None

    @property
    def status(self) -> str:
        if self.rejected_count:
            return (
                "completed_with_rejections"
            )

        return "completed"


def ingest_patients_csv(
    file_path: str | Path,
    rejection_output_dir: str | Path = (
        "data/rejected"
    ),
) -> PatientIngestionResult:
    """Insere pacientes válidos ainda inexistentes."""

    source_file = Path(
        file_path
    ).resolve()

    dataframe = read_csv_file(
        source_file
    )

    validation = (
        validate_patient_dataframe(
            dataframe
        )
    )

    rejection_file = (
        write_rejected_patient_report(
            rejected_records=(
                validation.rejected_records
            ),
            source_file=source_file,
            output_dir=(
                rejection_output_dir
            ),
        )
    )

    records = list(
        validation.valid_records
    )

    external_codes = [
        str(record["external_code"])
        for record in records
    ]

    existing_codes: set[str] = set()
    new_records = records

    try:
        with session_scope() as session:
            if external_codes:
                existing_statement = select(
                    Patient.external_code
                ).where(
                    Patient.external_code.in_(
                        external_codes
                    )
                )

                existing_codes = set(
                    session.scalars(
                        existing_statement
                    ).all()
                )

                new_records = [
                    record
                    for record in records
                    if record["external_code"]
                    not in existing_codes
                ]

            patients = [
                map_patient_record(record)
                for record in new_records
            ]

            session.add_all(patients)

    except SQLAlchemyError as error:
        raise PatientIngestionError(
            "Não foi possível inserir os "
            "pacientes válidos no PostgreSQL."
        ) from error

    return PatientIngestionResult(
        source_file=source_file,
        received_count=(
            validation.received_count
        ),
        valid_count=validation.valid_count,
        rejected_count=(
            validation.rejected_count
        ),
        inserted_count=len(new_records),
        existing_count=len(existing_codes),
        acceptance_rate=(
            validation.acceptance_rate
        ),
        warnings=validation.warnings,
        rejection_file=rejection_file,
    )