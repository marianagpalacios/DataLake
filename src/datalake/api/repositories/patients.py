from sqlalchemy import func, select
from sqlalchemy.orm import Session

from datalake.api.exceptions import (
    ResourceNotFoundError,
)
from datalake.models.patient import Patient


def list_patients(
    session: Session,
    *,
    offset: int,
    limit: int,
    external_code: str | None = None,
    biological_sex: str | None = None,
) -> tuple[list[Patient], int]:
    """Consulta pacientes com filtros e paginação."""

    conditions = []

    if external_code:
        conditions.append(Patient.external_code.ilike(f"%{external_code}%"))

    if biological_sex:
        conditions.append(Patient.biological_sex == biological_sex)

    count_statement = select(func.count()).select_from(Patient).where(*conditions)

    total = session.scalar(count_statement) or 0

    statement = (
        select(Patient)
        .where(*conditions)
        .order_by(Patient.id)
        .offset(offset)
        .limit(limit)
    )

    patients = list(session.scalars(statement))

    return patients, total


def get_patient(
    session: Session,
    patient_id: int,
) -> Patient:
    patient = session.get(
        Patient,
        patient_id,
    )

    if patient is None:
        raise ResourceNotFoundError(
            "Paciente",
            patient_id,
        )

    return patient
