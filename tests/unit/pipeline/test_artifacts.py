from datetime import date
from pathlib import Path
from uuid import uuid4

import pandas as pd

from datalake.pipeline.artifacts import (
    write_processed_patient_file,
)
from datalake.quality.models import ValidatedPatientRecord


def test_processed_file_returns_none_without_records(
    tmp_path: Path,
) -> None:
    result = write_processed_patient_file(
        valid_records=(),
        source_file=tmp_path / "patients.csv",
        run_uuid=uuid4(),
        output_dir=tmp_path / "processed",
    )

    assert result is None
    assert not (tmp_path / "processed").exists()


def test_processed_file_preserves_normalized_values(
    tmp_path: Path,
) -> None:
    validated = ValidatedPatientRecord(
        row_number=7,
        raw_record={
            "external_code": " PAT-001 ",
            "birth_date": "1995-04-10",
            "biological_sex": " FEMALE ",
        },
        normalized_record={
            "external_code": "PAT-001",
            "birth_date": date(1995, 4, 10),
            "biological_sex": "female",
        },
    )

    result = write_processed_patient_file(
        valid_records=(validated,),
        source_file=tmp_path / "patients.csv",
        run_uuid=uuid4(),
        output_dir=tmp_path / "processed",
    )

    assert result is not None
    assert result.is_file()

    dataframe = pd.read_csv(result, dtype=str)
    row = dataframe.iloc[0].to_dict()

    assert row == {
        "external_code": "PAT-001",
        "birth_date": "1995-04-10",
        "biological_sex": "female",
        "source_row_number": "7",
    }
    assert "datetime.date" not in result.read_text(encoding="utf-8")
