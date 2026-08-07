from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import delete, select
from sqlalchemy.orm import Session, sessionmaker

from datalake.ingestion.services import ingest_patients_csv
from datalake.models.patient import Patient


@pytest.mark.integration
def test_patient_ingestion_is_idempotent(
    tmp_path: Path,
    test_session_factory: sessionmaker[Session],
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
        first_result = ingest_patients_csv(
            file_path,
            session_factory=test_session_factory,
        )
        second_result = ingest_patients_csv(
            file_path,
            session_factory=test_session_factory,
        )

        assert first_result.received_count == 2
        assert first_result.valid_count == 2
        assert first_result.rejected_count == 0
        assert first_result.inserted_count == 2
        assert first_result.existing_count == 0

        assert second_result.received_count == 2
        assert second_result.inserted_count == 0
        assert second_result.existing_count == 2

        with test_session_factory() as session:
            statement = select(Patient).where(Patient.external_code.in_(codes))

            stored_patients = list(session.scalars(statement))

        assert len(stored_patients) == 2

    finally:
        with test_session_factory.begin() as session:
            session.execute(delete(Patient).where(Patient.external_code.in_(codes)))


@pytest.mark.integration
def test_patient_ingestion_inserts_only_valid_records(
    tmp_path: Path,
    test_session_factory: sessionmaker[Session],
) -> None:
    unique_suffix = uuid4().hex[:8].upper()
    codes = [
        f"TEST-{unique_suffix}-VALID",
        f"TEST-{unique_suffix}-INVALID-DATE",
        f"TEST-{unique_suffix}-INVALID-SEX",
    ]
    file_path = tmp_path / "patients_with_rejections.csv"
    rejection_dir = tmp_path / "rejected"

    file_path.write_text(
        "external_code,birth_date,biological_sex\n"
        f"{codes[0]},1995-04-10,female\n"
        f"{codes[1]},10/04/1995,male\n"
        f"{codes[2]},2000-01-01,invalid_value\n",
        encoding="utf-8",
    )

    try:
        result = ingest_patients_csv(
            file_path,
            rejection_output_dir=rejection_dir,
            session_factory=test_session_factory,
        )

        assert result.received_count == 3
        assert result.valid_count == 1
        assert result.rejected_count == 2
        assert result.inserted_count == 1
        assert result.rejection_file is not None
        assert result.rejection_file.is_file()
        assert result.rejection_file.parent == rejection_dir.resolve()

        with test_session_factory() as session:
            statement = select(Patient).where(Patient.external_code.in_(codes))
            stored_patients = list(session.scalars(statement))

        assert {patient.external_code for patient in stored_patients} == {codes[0]}

    finally:
        with test_session_factory.begin() as session:
            session.execute(delete(Patient).where(Patient.external_code.in_(codes)))
