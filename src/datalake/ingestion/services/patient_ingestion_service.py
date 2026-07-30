from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from datalake.database.session import session_scope
from datalake.ingestion.exceptions import PatientIngestionError
from datalake.ingestion.mappers import map_patient_record
from datalake.ingestion.readers import read_csv_file
from datalake.ingestion.validators import (
    validate_patient_dataframe,
)
from datalake.models.patient import Patient


@dataclass(frozen=True)
class PatientIngestionResult:
    """Resumo de uma ingestão de pacientes."""

    source_file: Path
    received_count: int
    inserted_count: int
    existing_count: int
    warnings: tuple[str, ...]


def ingest_patients_csv(
    file_path: str | Path,
) -> PatientIngestionResult:
    """Lê, valida e insere pacientes ainda inexistentes."""

    source_file = Path(file_path).resolve()

    dataframe = read_csv_file(source_file)
    validation = validate_patient_dataframe(dataframe)

    records = validation.dataframe.to_dict(
        orient="records"
    )

    external_codes = [
        str(record["external_code"])
        for record in records
    ]

    try:
        with session_scope() as session:
            existing_statement = select(
                Patient.external_code
            ).where(
                Patient.external_code.in_(external_codes)
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
            "Não foi possível inserir os pacientes "
            "no PostgreSQL."
        ) from error

    return PatientIngestionResult(
        source_file=source_file,
        received_count=len(records),
        inserted_count=len(new_records),
        existing_count=len(existing_codes),
        warnings=validation.warnings,
    )