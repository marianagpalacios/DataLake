from pathlib import Path

import pytest

from datalake.pipeline.exceptions import SourceFileError
from datalake.pipeline.files import (
    calculate_sha256,
    prepare_source_file,
)


def test_sha256_is_deterministic(tmp_path: Path) -> None:
    file_path = tmp_path / "patients.csv"
    file_path.write_text("same content", encoding="utf-8")

    first = calculate_sha256(file_path)
    second = calculate_sha256(file_path)

    assert first == second
    assert len(first) == 64


def test_sha256_changes_with_content(tmp_path: Path) -> None:
    first_file = tmp_path / "first.csv"
    second_file = tmp_path / "second.csv"
    first_file.write_text("first content", encoding="utf-8")
    second_file.write_text("second content", encoding="utf-8")

    assert calculate_sha256(first_file) != calculate_sha256(second_file)


def test_prepare_source_file_creates_raw_copy(
    tmp_path: Path,
) -> None:
    source = tmp_path / "patients.csv"
    source.write_text(
        "external_code\nPAT-001\n",
        encoding="utf-8",
    )

    prepared = prepare_source_file(
        source,
        raw_dir=tmp_path / "raw",
    )

    assert prepared.raw_path.is_file()
    assert prepared.size_bytes == source.stat().st_size
    assert prepared.raw_path.read_text(encoding="utf-8") == source.read_text(
        encoding="utf-8"
    )


def test_prepare_source_file_reuses_raw_copy(
    tmp_path: Path,
) -> None:
    source = tmp_path / "patients.csv"
    source.write_text("same content", encoding="utf-8")
    raw_dir = tmp_path / "raw"

    first = prepare_source_file(source, raw_dir=raw_dir)
    first.raw_path.write_text("preserved copy", encoding="utf-8")
    second = prepare_source_file(source, raw_dir=raw_dir)

    assert second.raw_path == first.raw_path
    assert second.raw_path.read_text(encoding="utf-8") == "preserved copy"


def test_prepare_source_file_rejects_missing_file(
    tmp_path: Path,
) -> None:
    with pytest.raises(SourceFileError, match="Arquivo não encontrado"):
        prepare_source_file(
            tmp_path / "missing.csv",
            raw_dir=tmp_path / "raw",
        )
