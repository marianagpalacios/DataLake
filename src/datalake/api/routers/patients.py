from typing import Annotated

from fastapi import APIRouter, Query

from datalake.api.dependencies import (
    PaginationDep,
    SessionDep,
)
from datalake.api.pagination import (
    Page,
    build_page,
)
from datalake.api.repositories.patients import (
    get_patient,
    list_patients,
)
from datalake.api.schemas import (
    BiologicalSex,
    PatientRead,
)

router = APIRouter(
    prefix="/patients",
    tags=["patients"],
)


@router.get(
    "",
    response_model=Page[PatientRead],
)
def read_patients(
    session: SessionDep,
    pagination: PaginationDep,
    external_code: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=50,
        ),
    ] = None,
    biological_sex: BiologicalSex | None = None,
) -> Page[PatientRead]:
    patients, total = list_patients(
        session,
        offset=pagination.offset,
        limit=pagination.size,
        external_code=external_code,
        biological_sex=biological_sex,
    )

    items = [PatientRead.model_validate(patient) for patient in patients]

    return build_page(
        items,
        total=total,
        page=pagination.page,
        size=pagination.size,
    )


@router.get(
    "/{patient_id}",
    response_model=PatientRead,
)
def read_patient(
    patient_id: int,
    session: SessionDep,
) -> PatientRead:
    patient = get_patient(
        session,
        patient_id,
    )

    return PatientRead.model_validate(patient)
