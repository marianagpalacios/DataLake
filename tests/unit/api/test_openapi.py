from fastapi.testclient import TestClient

from datalake.api.app import app


def test_openapi_contains_expected_routes() -> None:
    client = TestClient(app)

    response = client.get(
        "/openapi.json"
    )

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert "/health/live" in paths
    assert "/health/ready" in paths
    assert "/api/v1/patients" in paths
    assert "/api/v1/source-files" in paths
    assert "/api/v1/ingestion-runs" in paths