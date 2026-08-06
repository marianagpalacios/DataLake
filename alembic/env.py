from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

import datalake.models
from datalake.config import get_settings
from datalake.database.base import Base


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

MANAGED_SCHEMAS = {
    None,
    "public",
    "ingestion",
    "staging",
    "quality",
    "core",
}


def include_name(
    name: str | None,
    type_: str,
    parent_names: dict[str, str | None],
) -> bool:
    """Limita a comparação aos schemas gerenciados pelo projeto."""

    if type_ == "schema":
        return name in MANAGED_SCHEMAS

    return True


def run_migrations_offline() -> None:
    """Gera SQL sem abrir uma conexão ativa."""

    settings = get_settings()

    context.configure(
        url=settings.database_url.render_as_string(
            hide_password=False
        ),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_name=include_name,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa as migrações diretamente no PostgreSQL."""

    settings = get_settings()

    connectable = create_engine(
        settings.database_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_name=include_name,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()