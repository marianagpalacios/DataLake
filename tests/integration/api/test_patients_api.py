from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from datalake.database.session import (
    SessionFactory,
)
from datalake.models.patient import Patient


@pytest.mark.integration
def test_patient_can_be_retrieved(
    api_client: TestClient,
) -> None:
    external_code = (
        f"API-{uuid4().hex[:12].upper()}"
    )

    with SessionFactory.begin() as session:
        patient = Patient(
            external_code=external_code,
            biological_sex="unknown",
        )

        session.add(patient)
        session.flush()

        patient_id = patient.id

    try:
        response = api_client.get(
            f"/api/v1/patients/{patient_id}"
        )

        assert response.status_code == 200

        body = response.json()

        assert body["id"] == patient_id
        assert (
            body["external_code"]
            == external_code
        )
        assert (
            body["biological_sex"]
            == "unknown"
        )

    finally:
        with SessionFactory.begin() as session:
            session.execute(
                delete(Patient).where(
                    Patient.external_code
                    == external_code
                )
            )


@pytest.mark.integration
def test_missing_patient_returns_404(
    api_client: TestClient,
) -> None:
    response = api_client.get(
        "/api/v1/patients/999999999"
    )

    assert response.status_code == 404

    assert (
        response.json()["error"]["code"]
        == "resource_not_found"
    )


@pytest.mark.integration
def test_patient_pagination_is_validated(
    api_client: TestClient,
) -> None:
    response = api_client.get(
        "/api/v1/patients?page=0"
    )

    assert response.status_code == 422