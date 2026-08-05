from pathlib import Path

import pandas as pd

from datalake.quality.models import (
    DataQualityIssue,
    RejectedPatientRecord,
)
from datalake.quality.reports import write_rejected_patient_report


def _rejected_patient() -> RejectedPatientRecord:
    issue = DataQualityIssue(
        row_number=3,
        field="birth_date",
        code="invalid_date_format",
        message="A data deve usar o formato AAAA-MM-DD.",
        raw_value="10/04/1995",
    )

    return RejectedPatientRecord(
        row_number=3,
        raw_record={
            "external_code": "PAT-001",
            "birth_date": "10/04/1995",
            "biological_sex": "female",
        },
        issues=(issue,),
    )


def test_report_returns_none_when_there_are_no_rejections(
    tmp_path: Path,
) -> None:
    report_path = write_rejected_patient_report(
        rejected_records=(),
        source_file="patients.csv",
        output_dir=tmp_path / "rejected",
    )

    assert report_path is None


def test_report_creates_output_directory(tmp_path: Path) -> None:
    output_dir = tmp_path / "nested" / "rejected"

    report_path = write_rejected_patient_report(
        rejected_records=(_rejected_patient(),),
        source_file="patients.csv",
        output_dir=output_dir,
    )

    assert report_path is not None
    assert output_dir.is_dir()
    assert report_path.is_file()


def test_report_contains_issue_details(tmp_path: Path) -> None:
    report_path = write_rejected_patient_report(
        rejected_records=(_rejected_patient(),),
        source_file="patients.csv",
        output_dir=tmp_path,
    )

    assert report_path is not None

    report = pd.read_csv(report_path, dtype=str)
    row = report.iloc[0]

    assert row["external_code"] == "PAT-001"
    assert row["birth_date"] == "10/04/1995"
    assert row["biological_sex"] == "female"
    assert row["source_row_number"] == "3"
    assert row["error_codes"] == "invalid_date_format"
    assert row["error_fields"] == "birth_date"
    assert row["error_messages"] == (
        "A data deve usar o formato AAAA-MM-DD."
    )
