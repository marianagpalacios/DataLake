from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from datalake.database.session import SessionFactory


def get_session() -> Iterator[Session]:
    """Fornece uma sessão SQLAlchemy por requisição."""

    session = SessionFactory()

    try:
        yield session
    finally:
        session.close()


SessionDep = Annotated[
    Session,
    Depends(get_session),
]


class PaginationParams:
    """Parâmetros comuns de paginação."""

    def __init__(
        self,
        page: Annotated[
            int,
            Query(ge=1),
        ] = 1,
        size: Annotated[
            int,
            Query(ge=1, le=100),
        ] = 20,
    ) -> None:
        self.page = page
        self.size = size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


PaginationDep = Annotated[
    PaginationParams,
    Depends(),
]
