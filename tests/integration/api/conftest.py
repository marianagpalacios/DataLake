import pytest
from fastapi.testclient import TestClient

from datalake.api.app import app


@pytest.fixture
def api_client() -> TestClient:
    with TestClient(app) as client:
        yield client