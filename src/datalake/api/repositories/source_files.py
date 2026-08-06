from sqlalchemy import func, select
from sqlalchemy.orm import Session

from datalake.api.exceptions import (
    ResourceNotFoundError,
)
from datalake.models.source_file import SourceFile


def list_source_files(
    session: Session,
    *,
    offset: int,
    limit: int,
    data_source_id: int | None = None,
    original_name: str | None = None,
    sha256: str | None = None,
) -> tuple[list[SourceFile], int]:
    conditions = []

    if data_source_id is not None:
        conditions.append(
            SourceFile.data_source_id
            == data_source_id
        )

    if original_name:
        conditions.append(
            SourceFile.original_name.ilike(
                f"%{original_name}%"
            )
        )

    if sha256:
        conditions.append(
            SourceFile.sha256.startswith(
                sha256
            )
        )

    count_statement = (
        select(func.count())
        .select_from(SourceFile)
        .where(*conditions)
    )

    total = (
        session.scalar(count_statement)
        or 0
    )

    statement = (
        select(SourceFile)
        .where(*conditions)
        .order_by(SourceFile.id.desc())
        .offset(offset)
        .limit(limit)
    )

    files = list(
        session.scalars(statement)
    )

    return files, total


def get_source_file(
    session: Session,
    source_file_id: int,
) -> SourceFile:
    source_file = session.get(
        SourceFile,
        source_file_id,
    )

    if source_file is None:
        raise ResourceNotFoundError(
            "Arquivo de origem",
            source_file_id,
        )

    return source_file