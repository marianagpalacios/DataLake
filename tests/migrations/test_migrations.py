from pathlib import Path
from uuid import uuid4

import pytest
from alembic.config import Config
from sqlalchemy import (
    Engine,
    create_engine,
    inspect,
    text,
)

from alembic import command
from tests.conftest import (
    TestDatabaseSettings,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.migration
@pytest.mark.integration
def test_migrations_upgrade_downgrade_and_upgrade(
    test_database_settings: TestDatabaseSettings,
) -> None:
    database_name = f"datalake_migration_{uuid4().hex[:12]}"

    admin_url = test_database_settings.database_url.set(database="postgres")

    target_url = test_database_settings.database_url.set(database=database_name)

    admin_engine = create_engine(
        admin_url,
        isolation_level="AUTOCOMMIT",
    )

    target_engine: Engine | None = None

    try:
        with admin_engine.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{database_name}"'))

        target_engine = create_engine(target_url)

        config = Config(str(PROJECT_ROOT / "alembic.ini"))

        config.set_main_option(
            "script_location",
            str(PROJECT_ROOT / "alembic"),
        )

        with target_engine.begin() as connection:
            config.attributes["connection"] = connection

            command.upgrade(
                config,
                "head",
            )

        inspector = inspect(target_engine)

        assert inspector.has_table(
            "patients",
            schema="core",
        )

        assert inspector.has_table(
            "ingestion_runs",
            schema="ingestion",
        )

        assert inspector.has_table(
            "patient_records",
            schema="staging",
        )

        assert inspector.has_table(
            "data_quality_issues",
            schema="quality",
        )

        with target_engine.begin() as connection:
            config.attributes["connection"] = connection

            command.downgrade(
                config,
                "base",
            )

        inspector = inspect(target_engine)

        assert not inspector.has_table(
            "patients",
            schema="core",
        )

        with target_engine.begin() as connection:
            config.attributes["connection"] = connection

            command.upgrade(
                config,
                "head",
            )

        inspector = inspect(target_engine)

        assert inspector.has_table(
            "patients",
            schema="core",
        )

    finally:
        if target_engine is not None:
            target_engine.dispose()

        with admin_engine.connect() as connection:
            connection.execute(
                text(
                    """
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = :database_name
                      AND pid <> pg_backend_pid()
                    """
                ),
                {
                    "database_name": database_name,
                },
            )

            connection.execute(text(f'DROP DATABASE IF EXISTS "{database_name}"'))

        admin_engine.dispose()
