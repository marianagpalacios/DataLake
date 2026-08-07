from importlib.metadata import version

from fastapi import APIRouter, FastAPI

from datalake.api.handlers import (
    register_exception_handlers,
)
from datalake.api.routers import (
    health,
    ingestion_runs,
    patients,
    source_files,
    staged_records,
)


def create_app() -> FastAPI:
    """Cria e configura a aplicação."""

    app = FastAPI(
        title="DataLake API",
        description=(
            "API de consulta da plataforma educacional de engenharia de dados em saúde."
        ),
        version=version("datalake-health-platform"),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    register_exception_handlers(app)

    app.include_router(health.router)

    api_v1 = APIRouter(prefix="/api/v1")

    api_v1.include_router(patients.router)

    api_v1.include_router(source_files.router)

    api_v1.include_router(ingestion_runs.router)

    api_v1.include_router(staged_records.router)

    app.include_router(api_v1)

    @app.get(
        "/",
        include_in_schema=False,
    )
    def root() -> dict[str, str]:
        return {
            "service": "DataLake API",
            "documentation": "/docs",
            "health": "/health/ready",
        }

    return app


app = create_app()
