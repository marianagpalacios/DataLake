import pytest
from sqlalchemy import text

from datalake.database.engine import engine


@pytest.mark.integration
def test_database_connection() -> None:
    with engine.connect() as connection:
        result = connection.scalar(text("SELECT 1"))

    assert result == 1