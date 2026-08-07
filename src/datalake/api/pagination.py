from math import ceil
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

ItemType = TypeVar("ItemType")


class PageMeta(BaseModel):
    """Metadados de uma página de resultados."""

    page: int = Field(ge=1)
    size: int = Field(ge=1)
    total: int = Field(ge=0)
    pages: int = Field(ge=0)


class Page(BaseModel, Generic[ItemType]):
    """Resposta paginada genérica."""

    items: list[ItemType]
    meta: PageMeta


def build_page(
    items: list[ItemType],
    *,
    total: int,
    page: int,
    size: int,
) -> Page[ItemType]:
    """Monta uma resposta paginada."""

    pages = ceil(total / size) if total else 0

    return Page[ItemType](
        items=items,
        meta=PageMeta(
            page=page,
            size=size,
            total=total,
            pages=pages,
        ),
    )
