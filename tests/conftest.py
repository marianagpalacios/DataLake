from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from pydantic import SecretStr
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)
from sqlalchemy import Engine, URL, create_engine
from sqlalchemy.orm import Session, sessionmaker


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TestDatabaseSettings(BaseSettings):
    """Configurações exclusivas do banco de testes."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env.test",
        env_file_encoding="utf-8",
        env_prefix="TEST_",
        case_sensitive=False,
        extra="ignore",
    )

    postgres_db: str
    postgres_user: str
    postgres_password: SecretStr
    postgres_host: str = "localhost"
    postgres_port: int = 5433

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.postgres_user,
            password=(
                self.postgres_password
                .get_secret_value()
            ),
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )


@pytest.fixture(scope="session")
def test_database_settings() -> TestDatabaseSettings:
    settings = TestDatabaseSettings()

    database_name = settings.postgres_db.lower()

    if (
        database_name == "datalake"
        or not database_name.endswith("_test")
    ):
        pytest.exit(
            "Execução interrompida: o banco configurado "
            "não parece ser exclusivo de testes."
        )

    return settings


@pytest.fixture(scope="session")
def test_engine(
    test_database_settings: TestDatabaseSettings,
) -> Iterator[Engine]:
    engine = create_engine(
        test_database_settings.database_url,
        pool_pre_ping=True,
    )

    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture(scope="session")
def test_session_factory(
    test_engine: Engine,
) -> sessionmaker[Session]:
    return sessionmaker(
        bind=test_engine,
        class_=Session,
        autoflush=False,
        expire_on_commit=False,
    )


@pytest.fixture(scope="session")
def migrated_test_database(
    test_engine: Engine,
) -> Iterator[None]:
    alembic_config = Config(
        str(PROJECT_ROOT / "alembic.ini")
    )

    alembic_config.set_main_option(
        "script_location",
        str(PROJECT_ROOT / "alembic"),
    )

    with test_engine.begin() as connection:
        alembic_config.attributes[
            "connection"
        ] = connection

        command.upgrade(
            alembic_config,
            "head",
        )

    yield


def pytest_collection_modifyitems(
    items: list[pytest.Item],
) -> None:
    """Adiciona marcadores com base na pasta do teste."""

    for item in items:
        path_parts = set(item.path.parts)

        if "unit" in path_parts:
            item.add_marker(
                pytest.mark.unit
            )

        if "integration" in path_parts:
            item.add_marker(
                pytest.mark.integration
            )

        if "api" in path_parts:
            item.add_marker(
                pytest.mark.api
            )

        if "migrations" in path_parts:
            item.add_marker(
                pytest.mark.migration
            )