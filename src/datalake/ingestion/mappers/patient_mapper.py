from collections.abc import Mapping
from datetime import date

from datalake.models.patient import Patient


def map_patient_record(
    record: Mapping[str, object],
) -> Patient:
    """Converte um registro validado em um modelo Patient."""

    external_code = record.get("external_code")
    birth_date = record.get("birth_date")
    biological_sex = record.get("biological_sex")

    if not isinstance(external_code, str):
        raise TypeError("`external_code` deve ser um texto.")

    if birth_date is not None and not isinstance(birth_date, date):
        raise TypeError("`birth_date` deve ser uma data ou None.")

    if biological_sex is not None and not isinstance(biological_sex, str):
        raise TypeError("`biological_sex` deve ser um texto ou None.")

    return Patient(
        external_code=external_code,
        birth_date=birth_date,
        biological_sex=biological_sex,
    )
