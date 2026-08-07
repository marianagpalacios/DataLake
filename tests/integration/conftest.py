from collections.abc import Iterator

import pytest
from sqlalchemy import Engine, text

import datalake.models
from datalake.database.base import Base


def _qualified_table_name(table) -> str:
    if table.schema:
        return (
            f'"{table.schema}".'
            f'"{table.name}"'
        )

    return f'"{table.name}"'


def _truncate_all_tables(
    engine: Engine,
) -> None:
    table_names = ", ".join(
        _qualified_table_name(table)
        for table in Base.metadata.sorted_tables
    )

    if not table_names:
        return

    statement = text(
        "TRUNCATE TABLE "
        f"{table_names} "
        "RESTART IDENTITY CASCADE"
    )

    with engine.begin() as connection:
        connection.execute(statement)


@pytest.fixture(autouse=True)
def clean_test_database(
    migrated_test_database: None,
    test_engine: Engine,
) -> Iterator[None]:
    """Isola os dados de cada teste de integração."""

    _truncate_all_tables(test_engine)

    yield

    _truncate_all_tables(test_engine)