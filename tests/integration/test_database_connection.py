import pytest
from sqlalchemy import Engine, text


@pytest.mark.integration
def test_database_connection(
    test_engine: Engine,
    migrated_test_database: None,
) -> None:
    with test_engine.connect() as connection:
        result = connection.scalar(text("SELECT 1"))

    assert result == 1
