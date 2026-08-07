from collections.abc import Iterator
from importlib.metadata import version

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from datalake.api.dependencies import get_session


def test_liveness(
    api_client: TestClient,
) -> None:
    response = api_client.get("/health/live")

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "alive"
    assert body["service"] == "DataLake API"
    assert body["version"] == version("datalake-health-platform")


@pytest.mark.integration
def test_readiness(
    api_client: TestClient,
) -> None:
    response = api_client.get("/health/ready")

    assert response.status_code == 200

    assert response.json() == {
        "status": "ready",
        "database": "available",
    }


@pytest.mark.integration
def test_readiness_returns_503_when_database_is_unavailable(
    api_client: TestClient,
) -> None:
    def failing_session() -> Iterator[None]:
        raise OperationalError(
            statement="SELECT 1",
            params={},
            orig=Exception("simulated database failure"),
        )
        yield

    app = api_client.app
    previous_override = app.dependency_overrides.get(get_session)
    app.dependency_overrides[get_session] = failing_session

    try:
        response = api_client.get("/health/ready")
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(
                get_session,
                None,
            )
        else:
            app.dependency_overrides[get_session] = previous_override

    assert response.status_code == 503
    assert response.json()["error"]["code"] == ("database_unavailable")
