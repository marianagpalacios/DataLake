import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from tests.factories import (
    create_data_source,
    create_source_file,
)


@pytest.fixture
def source_files_data(
    test_session_factory: sessionmaker[Session],
) -> dict[str, object]:
    with test_session_factory.begin() as session:
        first_source = create_data_source(session)
        second_source = create_data_source(session)
        first_file = create_source_file(
            session,
            data_source=first_source,
            sha256="a" * 64,
            original_name="patients_january.csv",
        )
        second_file = create_source_file(
            session,
            data_source=first_source,
            sha256="b" * 64,
            original_name="patients_february.csv",
        )
        third_file = create_source_file(
            session,
            data_source=second_source,
            sha256="c" * 64,
            original_name="exams.csv",
        )

        return {
            "source_id": first_source.id,
            "file_ids": [
                first_file.id,
                second_file.id,
                third_file.id,
            ],
        }


@pytest.mark.integration
def test_source_files_support_pagination(
    api_client: TestClient,
    source_files_data: dict[str, object],
) -> None:
    response = api_client.get(
        "/api/v1/source-files?page=2&size=1"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["page"] == 2
    assert body["meta"]["size"] == 1
    assert body["meta"]["total"] == 3
    assert len(body["items"]) == 1


@pytest.mark.integration
def test_source_files_support_filters(
    api_client: TestClient,
    source_files_data: dict[str, object],
) -> None:
    source_id = source_files_data["source_id"]

    by_source = api_client.get(
        f"/api/v1/source-files?data_source_id={source_id}"
    ).json()
    by_name = api_client.get(
        "/api/v1/source-files?original_name=february"
    ).json()
    by_hash = api_client.get(
        f"/api/v1/source-files?sha256={'a' * 8}"
    ).json()

    assert by_source["meta"]["total"] == 2
    assert by_name["meta"]["total"] == 1
    assert by_name["items"][0]["original_name"] == (
        "patients_february.csv"
    )
    assert by_hash["meta"]["total"] == 1
    assert by_hash["items"][0]["sha256"] == "a" * 64


@pytest.mark.integration
def test_source_file_detail_hides_stored_path(
    api_client: TestClient,
    source_files_data: dict[str, object],
) -> None:
    source_file_id = source_files_data["file_ids"][0]
    response = api_client.get(
        f"/api/v1/source-files/{source_file_id}"
    )

    assert response.status_code == 200
    assert "stored_path" not in response.json()


@pytest.mark.integration
def test_missing_source_file_returns_404(
    api_client: TestClient,
) -> None:
    response = api_client.get(
        "/api/v1/source-files/999999"
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == (
        "resource_not_found"
    )
