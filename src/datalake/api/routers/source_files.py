from typing import Annotated

from fastapi import APIRouter, Query

from datalake.api.dependencies import (
    PaginationDep,
    SessionDep,
)
from datalake.api.pagination import (
    Page,
    build_page,
)
from datalake.api.repositories.source_files import (
    get_source_file,
    list_source_files,
)
from datalake.api.schemas import (
    SourceFileRead,
)

router = APIRouter(
    prefix="/source-files",
    tags=["source-files"],
)


@router.get(
    "",
    response_model=Page[SourceFileRead],
)
def read_source_files(
    session: SessionDep,
    pagination: PaginationDep,
    data_source_id: int | None = None,
    original_name: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=255,
        ),
    ] = None,
    sha256: Annotated[
        str | None,
        Query(
            min_length=4,
            max_length=64,
        ),
    ] = None,
) -> Page[SourceFileRead]:
    files, total = list_source_files(
        session,
        offset=pagination.offset,
        limit=pagination.size,
        data_source_id=data_source_id,
        original_name=original_name,
        sha256=sha256,
    )

    items = [SourceFileRead.model_validate(source_file) for source_file in files]

    return build_page(
        items,
        total=total,
        page=pagination.page,
        size=pagination.size,
    )


@router.get(
    "/{source_file_id}",
    response_model=SourceFileRead,
)
def read_source_file(
    source_file_id: int,
    session: SessionDep,
) -> SourceFileRead:
    source_file = get_source_file(
        session,
        source_file_id,
    )

    return SourceFileRead.model_validate(source_file)
