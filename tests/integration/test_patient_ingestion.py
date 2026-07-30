from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import delete, select

from datalake.database.session import SessionFactory
from datalake.ingestion.services import ingest_patients_csv
from datalake.models.patient import Patient


@pytest.mark.integration
def test_patient_ingestion_is_idempotent(
    tmp_path: Path,
) -> None:
    unique_suffix = uuid4().hex[:8].upper()

    codes = [
        f"TEST-{unique_suffix}-001",
        f"TEST-{unique_suffix}-002",
    ]

    file_path = tmp_path / "patients.csv"

    file_path.write_text(
        "external_code,birth_date,biological_sex\n"
        f"{codes[0]},1995-04-10,female\n"
        f"{codes[1]},,unknown\n",
        encoding="utf-8",
    )

    try:
        first_result = ingest_patients_csv(file_path)
        second_result = ingest_patients_csv(file_path)

        assert first_result.received_count == 2
        assert first_result.inserted_count == 2
        assert first_result.existing_count == 0

        assert second_result.received_count == 2
        assert second_result.inserted_count == 0
        assert second_result.existing_count == 2

        with SessionFactory() as session:
            statement = select(Patient).where(
                Patient.external_code.in_(codes)
            )

            stored_patients = list(
                session.scalars(statement)
            )

        assert len(stored_patients) == 2

    finally:
        with SessionFactory.begin() as session:
            session.execute(
                delete(Patient).where(
                    Patient.external_code.in_(codes)
                )
            )