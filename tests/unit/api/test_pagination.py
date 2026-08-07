from datalake.api.pagination import (
    build_page,
)


def test_build_page_calculates_pages() -> None:
    page = build_page(
        ["a", "b"],
        total=21,
        page=2,
        size=10,
    )

    assert page.items == ["a", "b"]
    assert page.meta.page == 2
    assert page.meta.size == 10
    assert page.meta.total == 21
    assert page.meta.pages == 3


def test_build_page_handles_empty_result() -> None:
    page = build_page(
        [],
        total=0,
        page=1,
        size=20,
    )

    assert page.items == []
    assert page.meta.total == 0
    assert page.meta.pages == 0
