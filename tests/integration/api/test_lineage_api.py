from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from datalake.database.session import SessionFactory
from datalake.models.data_quality_issue_record import (
    DataQualityIssueRecord,
)
from datalake.models.data_source import DataSource
from datalake.models.ingestion_run import IngestionRun
from datalake.models.source_file import SourceFile
from datalake.models.staged_patient_record import (
    StagedPatientRecord,
)


@pytest.mark.integration
def test_staged_record_lineage(
    api_client: TestClient,
) -> None:
    suffix = uuid4().hex
    source_name = f"lineage-api-test-{suffix}"
    expected_hash = suffix * 2
    source_id: int | None = None
    source_file_id: int | None = None

    try:
        with SessionFactory.begin() as session:
            source = DataSource(
                name=source_name,
                source_type="csv",
                description="Fonte temporária do teste de lineage.",
            )
            session.add(source)
            session.flush()
            source_id = source.id

            source_file = SourceFile(
                data_source_id=source.id,
                sha256=expected_hash,
                original_name="invalid_patients.csv",
                stored_path=(
                    "data/raw/invalid_patients.csv"
                ),
                size_bytes=128,
            )
            session.add(source_file)
            session.flush()
            source_file_id = source_file.id

            ingestion_run = IngestionRun(
                source_file_id=source_file.id,
                status="completed_with_rejections",
                pipeline_version="0.6.0",
                finished_at=datetime.now(timezone.utc),
                received_count=1,
                valid_count=0,
                rejected_count=1,
                inserted_count=0,
                existing_count=0,
                acceptance_rate=Decimal("0.00"),
            )
            session.add(ingestion_run)
            session.flush()

            staged_record = StagedPatientRecord(
                ingestion_run_id=ingestion_run.id,
                source_row_number=2,
                raw_record={
                    "external_code": "PAT-LINEAGE-INVALID",
                    "birth_date": "10/04/1995",
                    "biological_sex": "female",
                },
                normalized_external_code=(
                    "PAT-LINEAGE-INVALID"
                ),
                validation_status="rejected",
            )
            session.add(staged_record)
            session.flush()

            issue = DataQualityIssueRecord(
                staged_record_id=staged_record.id,
                field="birth_date",
                code="invalid_date_format",
                message=(
                    "A data deve usar o formato AAAA-MM-DD."
                ),
                raw_value="10/04/1995",
            )
            session.add(issue)
            record_id = staged_record.id

        response = api_client.get(
            f"/api/v1/staged-records/{record_id}/lineage"
        )
        body = response.json()

        assert response.status_code == 200
        assert body["record"]["validation_status"] == "rejected"
        assert (
            body["ingestion_run"]["status"]
            == "completed_with_rejections"
        )
        assert body["source_file"]["sha256"] == expected_hash
        assert body["patient"] is None
        assert body["issues"][0]["code"] == "invalid_date_format"

    finally:
        with SessionFactory.begin() as session:
            if source_file_id is not None:
                session.execute(
                    delete(SourceFile).where(
                        SourceFile.id == source_file_id
                    )
                )

            if source_id is not None:
                session.execute(
                    delete(DataSource).where(
                        DataSource.id == source_id
                    )
                )
