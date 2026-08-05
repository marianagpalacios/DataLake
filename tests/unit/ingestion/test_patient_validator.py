from datetime import date

import pandas as pd
import pytest

from datalake.ingestion.exceptions import PatientValidationError
from datalake.ingestion.validators import validate_patient_dataframe


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

    assert result.valid_records == (
        {
            "external_code": "PAT-001",
            "birth_date": date(1995, 4, 10),
            "biological_sex": "female",
        },
    )
    assert result.rejected_records == ()
    assert result.received_count == 1
    assert result.valid_count == 1
    assert result.rejected_count == 0
    assert result.acceptance_rate == 100.0
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

    assert result.valid_records == (
        {
            "external_code": "PAT-001",
            "birth_date": None,
            "biological_sex": None,
        },
    )
    assert result.rejected_records == ()
    assert result.received_count == 1
    assert result.valid_count == 1
    assert result.rejected_count == 0
    assert result.acceptance_rate == 100.0


def test_validator_rejects_missing_required_column() -> None:
    dataframe = pd.DataFrame([{"external_code": "PAT-001"}])

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

    result = validate_patient_dataframe(dataframe)

    assert result.valid_records == ()
    assert len(result.rejected_records) == 1
    assert {
        issue.code for issue in result.rejected_records[0].issues
    } == {"required_value_missing"}
    assert result.received_count == 1
    assert result.valid_count == 0
    assert result.rejected_count == 1
    assert result.acceptance_rate == 0.0


def test_validator_rejects_all_duplicate_codes() -> None:
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

    result = validate_patient_dataframe(dataframe)

    assert result.valid_records == ()
    assert len(result.rejected_records) == 2
    assert [
        {issue.code for issue in rejected.issues}
        for rejected in result.rejected_records
    ] == [{"duplicate_in_file"}, {"duplicate_in_file"}]
    assert result.received_count == 2
    assert result.valid_count == 0
    assert result.rejected_count == 2
    assert result.acceptance_rate == 0.0


def test_validator_rejects_invalid_date_format() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "external_code": "PAT-001",
                "birth_date": "10/04/1995",
                "biological_sex": "female",
            }
        ]
    )

    result = validate_patient_dataframe(dataframe)

    assert result.valid_records == ()
    assert {
        issue.code for issue in result.rejected_records[0].issues
    } == {"invalid_date_format"}
    assert result.received_count == 1
    assert result.valid_count == 0
    assert result.rejected_count == 1
    assert result.acceptance_rate == 0.0


def test_validator_rejects_future_birth_date() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "external_code": "PAT-001",
                "birth_date": "2025-01-02",
                "biological_sex": "female",
            }
        ]
    )

    result = validate_patient_dataframe(dataframe, today=date(2025, 1, 1))

    assert result.valid_records == ()
    assert {
        issue.code for issue in result.rejected_records[0].issues
    } == {"future_birth_date"}
    assert result.received_count == 1
    assert result.valid_count == 0
    assert result.rejected_count == 1
    assert result.acceptance_rate == 0.0


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

    result = validate_patient_dataframe(dataframe)

    assert result.valid_records == ()
    assert {
        issue.code for issue in result.rejected_records[0].issues
    } == {"invalid_biological_sex"}
    assert result.received_count == 1
    assert result.valid_count == 0
    assert result.rejected_count == 1
    assert result.acceptance_rate == 0.0


def test_validator_separates_valid_and_invalid_records() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "external_code": "PAT-VALID",
                "birth_date": "1995-04-10",
                "biological_sex": "female",
            },
            {
                "external_code": "",
                "birth_date": "1990-01-01",
                "biological_sex": "male",
            },
        ]
    )

    result = validate_patient_dataframe(dataframe)

    assert len(result.valid_records) == 1
    assert result.valid_records[0]["external_code"] == "PAT-VALID"
    assert len(result.rejected_records) == 1
    assert {
        issue.code for issue in result.rejected_records[0].issues
    } == {"required_value_missing"}
    assert result.received_count == 2
    assert result.valid_count == 1
    assert result.rejected_count == 1
    assert result.acceptance_rate == 50.0


def test_validator_warns_about_extra_column() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "external_code": "PAT-001",
                "birth_date": "1995-04-10",
                "biological_sex": "female",
                "source_system": "laboratory",
            }
        ]
    )

    result = validate_patient_dataframe(dataframe)

    assert len(result.valid_records) == 1
    assert result.rejected_records == ()
    assert result.received_count == 1
    assert result.valid_count == 1
    assert result.rejected_count == 0
    assert result.acceptance_rate == 100.0
    assert any("source_system" in warning for warning in result.warnings)
