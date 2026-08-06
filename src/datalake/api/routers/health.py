from importlib.metadata import version

from fastapi import APIRouter
from sqlalchemy import text

from datalake.api.dependencies import SessionDep
from datalake.api.schemas import (
    LivenessResponse,
    ReadinessResponse,
)


router = APIRouter(
    tags=["health"],
)


def get_project_version() -> str:
    return version(
        "datalake-health-platform"
    )


@router.get(
    "/health/live",
    response_model=LivenessResponse,
)
def liveness() -> LivenessResponse:
    return LivenessResponse(
        status="alive",
        service="DataLake API",
        version=get_project_version(),
    )


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
)
def readiness(
    session: SessionDep,
) -> ReadinessResponse:
    result = session.scalar(
        text("SELECT 1")
    )

    if result != 1:
        raise RuntimeError(
            "Resposta inesperada do banco."
        )

    return ReadinessResponse(
        status="ready",
        database="available",
    )