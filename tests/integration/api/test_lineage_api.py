import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from tests.factories import (
    create_data_source,
    create_ingestion_run,
    create_patient,
    create_quality_issue,
    create_source_file,
    create_staged_record,
)


@pytest.mark.integration
def test_valid_staged_record_lineage_contains_patient(
    api_client: TestClient,
    test_session_factory: sessionmaker[Session],
) -> None:
    with test_session_factory.begin() as session:
        source = create_data_source(session)
        source_file = create_source_file(
            session,
            data_source=source,
        )
        run = create_ingestion_run(
            session,
            source_file=source_file,
        )
        patient = create_patient(session)
        record = create_staged_record(
            session,
            run=run,
            patient=patient,
        )
        record_id = record.id
        expected_external_code = patient.external_code

    response = api_client.get(
        f"/api/v1/staged-records/{record_id}/lineage"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["record"]["validation_status"] == "valid"
    assert body["patient"]["external_code"] == (
        expected_external_code
    )
    assert body["issues"] == []


@pytest.mark.integration
def test_rejected_staged_record_lineage_contains_issues(
    api_client: TestClient,
    test_session_factory: sessionmaker[Session],
) -> None:
    expected_hash = "f" * 64

    with test_session_factory.begin() as session:
        source = create_data_source(session)
        source_file = create_source_file(
            session,
            data_source=source,
            sha256=expected_hash,
        )
        run = create_ingestion_run(
            session,
            source_file=source_file,
            status="completed_with_rejections",
            received_count=1,
            valid_count=0,
            rejected_count=1,
            inserted_count=0,
        )
        record = create_staged_record(
            session,
            run=run,
            validation_status="rejected",
        )
        create_quality_issue(
            session,
            staged_record=record,
        )
        record_id = record.id

    response = api_client.get(
        f"/api/v1/staged-records/{record_id}/lineage"
    )
    body = response.json()

    assert response.status_code == 200
    assert body["record"]["validation_status"] == "rejected"
    assert body["ingestion_run"]["status"] == (
        "completed_with_rejections"
    )
    assert body["source_file"]["sha256"] == expected_hash
    assert body["patient"] is None
    assert body["issues"][0]["code"] == "invalid_date_format"
    assert "raw_record" not in body["record"]
    assert "raw_value" not in body["issues"][0]
