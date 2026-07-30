from datetime import date

import pandas as pd
import pytest

from datalake.ingestion.exceptions import PatientValidationError
from datalake.ingestion.validators import (
    validate_patient_dataframe,
)


def test_validator_normalizes_patient_values() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "external_code": " PAT-001 ",
                "birth_date": " 1995-04-10 ",
                "biological_sex": " FEMALE ",
            }
        ]
    )

    result = validate_patient_dataframe(dataframe)
    record = result.dataframe.iloc[0]

    assert record["external_code"] == "PAT-001"
    assert record["birth_date"] == date(1995, 4, 10)
    assert record["biological_sex"] == "female"
    assert result.warnings


def test_validator_accepts_blank_optional_values() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "external_code": "PAT-001",
                "birth_date": "",
                "biological_sex": "",
            }
        ]
    )

    result = validate_patient_dataframe(dataframe)
    record = result.dataframe.iloc[0]

    assert record["birth_date"] is None
    assert record["biological_sex"] is None


def test_validator_rejects_missing_columns() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "external_code": "PAT-001",
            }
        ]
    )

    with pytest.raises(
        PatientValidationError,
        match="Colunas obrigatórias ausentes",
    ):
        validate_patient_dataframe(dataframe)


def test_validator_rejects_blank_external_code() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "external_code": " ",
                "birth_date": "1995-04-10",
                "biological_sex": "female",
            }
        ]
    )

    with pytest.raises(
        PatientValidationError,
        match="Código externo vazio",
    ):
        validate_patient_dataframe(dataframe)


def test_validator_rejects_duplicate_codes() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "external_code": "PAT-001",
                "birth_date": "1995-04-10",
                "biological_sex": "female",
            },
            {
                "external_code": "PAT-001",
                "birth_date": "2000-01-01",
                "biological_sex": "male",
            },
        ]
    )

    with pytest.raises(
        PatientValidationError,
        match="duplicados",
    ):
        validate_patient_dataframe(dataframe)


def test_validator_rejects_invalid_date() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "external_code": "PAT-001",
                "birth_date": "10/04/1995",
                "biological_sex": "female",
            }
        ]
    )

    with pytest.raises(
        PatientValidationError,
        match="Datas inválidas",
    ):
        validate_patient_dataframe(dataframe)


def test_validator_rejects_invalid_biological_sex() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "external_code": "PAT-001",
                "birth_date": "1995-04-10",
                "biological_sex": "invalid_value",
            }
        ]
    )

    with pytest.raises(
        PatientValidationError,
        match="biological_sex",
    ):
        validate_patient_dataframe(dataframe)