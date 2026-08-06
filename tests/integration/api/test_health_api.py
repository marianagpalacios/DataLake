import pytest
from fastapi.testclient import TestClient


def test_liveness(
    api_client: TestClient,
) -> None:
    response = api_client.get(
        "/health/live"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "alive"
    assert body["service"] == "DataLake API"


@pytest.mark.integration
def test_readiness(
    api_client: TestClient,
) -> None:
    response = api_client.get(
        "/health/ready"
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "ready",
        "database": "available",
    }