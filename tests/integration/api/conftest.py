from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from datalake.api.app import create_app
from datalake.api.dependencies import (
    get_session,
)


@pytest.fixture
def api_client(
    test_session_factory: sessionmaker[Session],
    migrated_test_database: None,
) -> Iterator[TestClient]:
    app = create_app()

    def override_get_session() -> Iterator[Session]:
        session = test_session_factory()

        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[
        get_session
    ] = override_get_session

    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()