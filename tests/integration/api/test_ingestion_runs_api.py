from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from tests.factories import (
    create_data_source,
    create_ingestion_run,
    create_quality_issue,
    create_source_file,
    create_staged_record,
)


@pytest.fixture
def ingestion_data(
    test_session_factory: sessionmaker[Session],
) -> dict[str, object]:
    with test_session_factory.begin() as session:
        source = create_data_source(session)
        first_file = create_source_file(
            session,
            data_source=source,
            sha256="d" * 64,
        )
        second_file = create_source_file(
            session,
            data_source=source,
            sha256="e" * 64,
            original_name="second.csv",
        )
        first_run = create_ingestion_run(
            session,
            source_file=first_file,
            status="completed_with_rejections",
            received_count=3,
            valid_count=1,
            rejected_count=2,
            inserted_count=1,
            started_at=datetime(
                2026, 1, 10, tzinfo=timezone.utc
            ),
            error_message="internal failure detail",
            processed_file_path="data/processed/patients.csv",
            rejection_file_path="data/rejected/patients.csv",
        )
        second_run = create_ingestion_run(
            session,
            source_file=second_file,
            started_at=datetime(
                2026, 2, 10, tzinfo=timezone.utc
            ),
        )

        valid_record = create_staged_record(
            session,
            run=first_run,
            source_row_number=2,
        )
        rejected_record = create_staged_record(
            session,
            run=first_run,
            validation_status="rejected",
            source_row_number=3,
        )
        another_rejected_record = create_staged_record(
            session,
            run=first_run,
            validation_status="rejected",
            source_row_number=4,
        )
        create_quality_issue(
            session,
            staged_record=rejected_record,
            code="invalid_date_format",
            field="birth_date",
        )
        create_quality_issue(
            session,
            staged_record=another_rejected_record,
            code="required_value",
            field="external_code",
        )

        return {
            "first_file_id": first_file.id,
            "first_run_uuid": str(first_run.run_uuid),
            "second_run_uuid": str(second_run.run_uuid),
            "valid_record_id": valid_record.id,
        }


@pytest.mark.integration
def test_ingestion_runs_support_filters_and_pagination(
    api_client: TestClient,
    ingestion_data: dict[str, object],
) -> None:
    file_id = ingestion_data["first_file_id"]
    by_status = api_client.get(
        "/api/v1/ingestion-runs?status=completed_with_rejections"
    ).json()
    by_file = api_client.get(
        f"/api/v1/ingestion-runs?source_file_id={file_id}"
    ).json()
    by_date = api_client.get(
        "/api/v1/ingestion-runs"
        "?started_from=2026-02-01T00:00:00Z"
        "&started_to=2026-02-28T23:59:59Z"
    ).json()
    paged = api_client.get(
        "/api/v1/ingestion-runs?page=2&size=1"
    ).json()

    assert by_status["meta"]["total"] == 1
    assert by_file["meta"]["total"] == 1
    assert by_date["meta"]["total"] == 1
    assert by_date["items"][0]["run_uuid"] == (
        ingestion_data["second_run_uuid"]
    )
    assert paged["meta"]["page"] == 2
    assert paged["meta"]["size"] == 1
    assert paged["meta"]["total"] == 2


@pytest.mark.integration
def test_ingestion_run_detail_hides_internal_fields(
    api_client: TestClient,
    ingestion_data: dict[str, object],
) -> None:
    response = api_client.get(
        "/api/v1/ingestion-runs/"
        f"{ingestion_data['first_run_uuid']}"
    )

    assert response.status_code == 200
    body = response.json()
    assert "error_message" not in body
    assert "processed_file_path" not in body
    assert "rejection_file_path" not in body


@pytest.mark.integration
def test_ingestion_run_rejects_invalid_or_missing_uuid(
    api_client: TestClient,
) -> None:
    invalid = api_client.get(
        "/api/v1/ingestion-runs/not-a-uuid"
    )
    missing = api_client.get(
        f"/api/v1/ingestion-runs/{uuid4()}"
    )

    assert invalid.status_code == 422
    assert missing.status_code == 404


@pytest.mark.integration
def test_run_records_support_status_and_pagination(
    api_client: TestClient,
    ingestion_data: dict[str, object],
) -> None:
    path = (
        "/api/v1/ingestion-runs/"
        f"{ingestion_data['first_run_uuid']}/records"
    )
    valid = api_client.get(
        f"{path}?validation_status=valid"
    ).json()
    rejected = api_client.get(
        f"{path}?validation_status=rejected"
    ).json()
    paged = api_client.get(
        f"{path}?page=2&size=1"
    ).json()

    assert valid["meta"]["total"] == 1
    assert valid["items"][0]["validation_status"] == "valid"
    assert rejected["meta"]["total"] == 2
    assert all(
        item["validation_status"] == "rejected"
        for item in rejected["items"]
    )
    assert paged["meta"]["page"] == 2
    assert len(paged["items"]) == 1
    assert "raw_record" not in paged["items"][0]


@pytest.mark.integration
def test_records_for_missing_run_return_404(
    api_client: TestClient,
) -> None:
    response = api_client.get(
        f"/api/v1/ingestion-runs/{uuid4()}/records"
    )

    assert response.status_code == 404


@pytest.mark.integration
def test_quality_issues_support_filters_and_pagination(
    api_client: TestClient,
    ingestion_data: dict[str, object],
) -> None:
    path = (
        "/api/v1/ingestion-runs/"
        f"{ingestion_data['first_run_uuid']}/quality-issues"
    )
    by_code = api_client.get(
        f"{path}?code=invalid_date_format"
    ).json()
    by_field = api_client.get(
        f"{path}?field=external_code"
    ).json()
    paged = api_client.get(
        f"{path}?page=2&size=1"
    ).json()

    assert by_code["meta"]["total"] == 1
    assert by_code["items"][0]["code"] == "invalid_date_format"
    assert by_field["meta"]["total"] == 1
    assert by_field["items"][0]["field"] == "external_code"
    assert paged["meta"]["page"] == 2
    assert len(paged["items"]) == 1
    assert "raw_value" not in paged["items"][0]
