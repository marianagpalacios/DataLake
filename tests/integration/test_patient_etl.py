from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, sessionmaker

from datalake.models.data_quality_issue_record import (
    DataQualityIssueRecord,
)
from datalake.models.data_source import DataSource
from datalake.models.ingestion_run import IngestionRun
from datalake.models.patient import Patient
from datalake.models.source_file import SourceFile
from datalake.models.staged_patient_record import StagedPatientRecord
from datalake.pipeline.exceptions import PatientETLError
from datalake.pipeline.patient_etl import run_patient_etl


def _test_identity() -> tuple[str, str]:
    suffix = uuid4().hex[:10].upper()
    return f"etl-test-{suffix}", f"ETL-{suffix}"


def _cleanup(
    session_factory: sessionmaker[Session],
    source_name: str,
    code_prefix: str,
) -> None:
    with session_factory.begin() as session:
        source = session.scalar(
            select(DataSource).where(DataSource.name == source_name)
        )

        if source is not None:
            session.execute(
                delete(SourceFile).where(SourceFile.data_source_id == source.id)
            )

        session.execute(
            delete(Patient).where(Patient.external_code.like(f"{code_prefix}%"))
        )

        if source is not None:
            session.delete(source)


@pytest.mark.integration
def test_patient_etl_persists_complete_lineage(
    tmp_path: Path,
    test_session_factory: sessionmaker[Session],
) -> None:
    source_name, code_prefix = _test_identity()
    file_path = tmp_path / "patients.csv"
    file_path.write_text(
        "external_code,birth_date,biological_sex\n"
        f"{code_prefix}-VALID,1995-04-10,female\n"
        f"{code_prefix}-DATE,10/04/1995,male\n"
        f"{code_prefix}-SEX,2000-01-01,invalid\n",
        encoding="utf-8",
    )

    try:
        result = run_patient_etl(
            file_path,
            source_name=source_name,
            raw_dir=tmp_path / "raw",
            processed_dir=tmp_path / "processed",
            rejected_dir=tmp_path / "rejected",
            session_factory=test_session_factory,
        )

        assert result.status == "completed_with_rejections"
        assert result.processed_file is not None
        assert result.processed_file.is_file()
        assert result.rejection_file is not None
        assert result.rejection_file.is_file()

        with test_session_factory() as session:
            run = session.scalar(
                select(IngestionRun).where(IngestionRun.run_uuid == result.run_uuid)
            )
            assert run is not None
            assert run.status == "completed_with_rejections"
            assert run.source_file is not None
            assert run.source_file.sha256 == result.source_sha256

            staged_count = session.scalar(
                select(func.count())
                .select_from(StagedPatientRecord)
                .where(StagedPatientRecord.ingestion_run_id == run.id)
            )
            issue_count = session.scalar(
                select(func.count())
                .select_from(DataQualityIssueRecord)
                .join(StagedPatientRecord)
                .where(StagedPatientRecord.ingestion_run_id == run.id)
            )
            patient_count = session.scalar(
                select(func.count())
                .select_from(Patient)
                .where(Patient.external_code.like(f"{code_prefix}%"))
            )

        assert staged_count == 3
        assert issue_count == 2
        assert patient_count == 1

    finally:
        _cleanup(
            test_session_factory,
            source_name,
            code_prefix,
        )


@pytest.mark.integration
def test_patient_etl_skips_duplicate_file(
    tmp_path: Path,
    test_session_factory: sessionmaker[Session],
) -> None:
    source_name, code_prefix = _test_identity()
    file_path = tmp_path / "patients.csv"
    file_path.write_text(
        "external_code,birth_date,biological_sex\n"
        f"{code_prefix}-001,1995-04-10,female\n"
        f"{code_prefix}-002,,unknown\n",
        encoding="utf-8",
    )

    try:
        first = run_patient_etl(
            file_path,
            source_name=source_name,
            raw_dir=tmp_path / "raw",
            processed_dir=tmp_path / "processed",
            rejected_dir=tmp_path / "rejected",
            session_factory=test_session_factory,
        )
        second = run_patient_etl(
            file_path,
            source_name=source_name,
            raw_dir=tmp_path / "raw",
            processed_dir=tmp_path / "processed",
            rejected_dir=tmp_path / "rejected",
            session_factory=test_session_factory,
        )

        assert first.status == "completed"
        assert second.status == "skipped_duplicate"
        assert second.duplicate_of_run_uuid == first.run_uuid

        with test_session_factory() as session:
            runs = list(
                session.scalars(
                    select(IngestionRun)
                    .join(SourceFile)
                    .join(DataSource)
                    .where(DataSource.name == source_name)
                    .order_by(IngestionRun.id)
                )
            )
            staged_counts = [
                session.scalar(
                    select(func.count())
                    .select_from(StagedPatientRecord)
                    .where(StagedPatientRecord.ingestion_run_id == run.id)
                )
                for run in runs
            ]

        assert len(runs) == 2
        assert runs[1].duplicate_of_run_id == runs[0].id
        assert staged_counts == [2, 0]

    finally:
        _cleanup(
            test_session_factory,
            source_name,
            code_prefix,
        )


@pytest.mark.integration
def test_patient_etl_force_reprocesses_file(
    tmp_path: Path,
    test_session_factory: sessionmaker[Session],
) -> None:
    source_name, code_prefix = _test_identity()
    file_path = tmp_path / "patients.csv"
    file_path.write_text(
        "external_code,birth_date,biological_sex\n"
        f"{code_prefix}-001,1995-04-10,female\n"
        f"{code_prefix}-002,,unknown\n",
        encoding="utf-8",
    )

    try:
        first = run_patient_etl(
            file_path,
            source_name=source_name,
            raw_dir=tmp_path / "raw",
            processed_dir=tmp_path / "processed",
            rejected_dir=tmp_path / "rejected",
            session_factory=test_session_factory,
        )
        forced = run_patient_etl(
            file_path,
            source_name=source_name,
            raw_dir=tmp_path / "raw",
            processed_dir=tmp_path / "processed",
            rejected_dir=tmp_path / "rejected",
            force=True,
            session_factory=test_session_factory,
        )

        assert first.status == "completed"
        assert forced.status == "completed"
        assert forced.run_uuid != first.run_uuid
        assert forced.inserted_count == 0
        assert forced.existing_count == 2

        with test_session_factory() as session:
            staged_count = session.scalar(
                select(func.count())
                .select_from(StagedPatientRecord)
                .join(IngestionRun)
                .join(SourceFile)
                .join(DataSource)
                .where(DataSource.name == source_name)
            )
            patient_count = session.scalar(
                select(func.count())
                .select_from(Patient)
                .where(Patient.external_code.like(f"{code_prefix}%"))
            )

        assert staged_count == 4
        assert patient_count == 2

    finally:
        _cleanup(
            test_session_factory,
            source_name,
            code_prefix,
        )


@pytest.mark.integration
def test_patient_etl_marks_structural_failure(
    tmp_path: Path,
    test_session_factory: sessionmaker[Session],
) -> None:
    source_name, code_prefix = _test_identity()
    file_path = tmp_path / "patients.csv"
    file_path.write_text(
        f"external_code,birth_date\n{code_prefix}-001,1995-04-10\n",
        encoding="utf-8",
    )

    try:
        with pytest.raises(PatientETLError):
            run_patient_etl(
                file_path,
                source_name=source_name,
                raw_dir=tmp_path / "raw",
                processed_dir=tmp_path / "processed",
                rejected_dir=tmp_path / "rejected",
                session_factory=test_session_factory,
            )

        with test_session_factory() as session:
            run = session.scalar(
                select(IngestionRun)
                .join(SourceFile)
                .join(DataSource)
                .where(DataSource.name == source_name)
            )
            assert run is not None

            staged_count = session.scalar(
                select(func.count())
                .select_from(StagedPatientRecord)
                .where(StagedPatientRecord.ingestion_run_id == run.id)
            )
            patient_count = session.scalar(
                select(func.count())
                .select_from(Patient)
                .where(Patient.external_code.like(f"{code_prefix}%"))
            )

        assert run.status == "failed"
        assert run.error_message
        assert staged_count == 0
        assert patient_count == 0

    finally:
        _cleanup(
            test_session_factory,
            source_name,
            code_prefix,
        )
