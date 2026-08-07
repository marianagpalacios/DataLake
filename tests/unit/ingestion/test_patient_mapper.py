from datetime import date

from datalake.ingestion.mappers import map_patient_record


def test_mapper_creates_patient_model() -> None:
    patient = map_patient_record(
        {
            "external_code": "PAT-001",
            "birth_date": date(1995, 4, 10),
            "biological_sex": "female",
        }
    )

    assert patient.external_code == "PAT-001"
    assert patient.birth_date == date(1995, 4, 10)
    assert patient.biological_sex == "female"


def test_mapper_accepts_optional_values() -> None:
    patient = map_patient_record(
        {
            "external_code": "PAT-002",
            "birth_date": None,
            "biological_sex": None,
        }
    )

    assert patient.external_code == "PAT-002"
    assert patient.birth_date is None
    assert patient.biological_sex is None
