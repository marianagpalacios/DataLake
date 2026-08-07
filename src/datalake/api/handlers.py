from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from datalake.api.exceptions import (
    ResourceNotFoundError,
)


def register_exception_handlers(
    app: FastAPI,
) -> None:
    """Registra handlers globais da API."""

    @app.exception_handler(ResourceNotFoundError)
    def handle_not_found(
        request: Request,
        error: ResourceNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "resource_not_found",
                    "message": str(error),
                }
            },
        )

    @app.exception_handler(SQLAlchemyError)
    def handle_database_error(
        request: Request,
        error: SQLAlchemyError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "code": "database_unavailable",
                    "message": ("O banco de dados não está disponível."),
                }
            },
        )
