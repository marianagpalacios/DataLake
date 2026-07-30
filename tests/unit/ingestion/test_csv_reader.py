from pathlib import Path

import pytest

from datalake.ingestion.exceptions import CSVReadError
from datalake.ingestion.readers import read_csv_file


def test_read_csv_file_returns_dataframe(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "patients.csv"

    file_path.write_text(
        "external_code,birth_date,biological_sex\n"
        "PAT-001,1995-04-10,female\n",
        encoding="utf-8",
    )

    dataframe = read_csv_file(file_path)

    assert list(dataframe.columns) == [
        "external_code",
        "birth_date",
        "biological_sex",
    ]

    assert len(dataframe) == 1
    assert dataframe.loc[0, "external_code"] == "PAT-001"


def test_read_csv_file_rejects_missing_file(
    tmp_path: Path,
) -> None:
    missing_file = tmp_path / "missing.csv"

    with pytest.raises(
        CSVReadError,
        match="não encontrado",
    ):
        read_csv_file(missing_file)


def test_read_csv_file_rejects_empty_file(
    tmp_path: Path,
) -> None:
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("", encoding="utf-8")

    with pytest.raises(
        CSVReadError,
        match="vazio",
    ):
        read_csv_file(empty_file)


def test_read_csv_file_rejects_malformed_csv(
    tmp_path: Path,
) -> None:
    malformed_file = tmp_path / "malformed.csv"

    malformed_file.write_text(
        "external_code,birth_date,biological_sex\n"
        "\"PAT-001,1995-04-10,female\n",
        encoding="utf-8",
    )

    with pytest.raises(
        CSVReadError,
        match="malformado",
    ):
        read_csv_file(malformed_file)