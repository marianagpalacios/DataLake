from pathlib import Path

from datalake.database.session import (
    SessionFactory,
    SessionFactoryType,
)
from datalake.pipeline import (
    PatientETLResult,
    run_patient_etl,
)


PatientIngestionResult = PatientETLResult


def ingest_patients_csv(
    file_path: str | Path,
    rejection_output_dir: str | Path = "data/rejected",
    session_factory: SessionFactoryType = SessionFactory,
) -> PatientETLResult:
    """Compatibilidade com a interface dos MVPs anteriores."""

    return run_patient_etl(
        file_path=file_path,
        rejected_dir=rejection_output_dir,
        session_factory=session_factory,
    )