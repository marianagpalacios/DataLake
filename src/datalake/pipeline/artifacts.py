from pathlib import Path
from uuid import UUID

import pandas as pd

from datalake.pipeline.exceptions import PipelineArtifactError
from datalake.quality.models import ValidatedPatientRecord


def write_processed_patient_file(
    valid_records: tuple[ValidatedPatientRecord, ...],
    source_file: str | Path,
    run_uuid: UUID,
    output_dir: str | Path = "data/processed",
) -> Path | None:
    """Grava os registros normalizados aceitos."""

    if not valid_records:
        return None

    source_path = Path(source_file)
    target_dir = Path(output_dir)

    rows: list[dict[str, object]] = []

    for validated in valid_records:
        record = validated.normalized_record
        birth_date = record.get("birth_date")

        rows.append(
            {
                "external_code": record["external_code"],
                "birth_date": (
                    birth_date.isoformat() if birth_date is not None else ""
                ),
                "biological_sex": (record.get("biological_sex") or ""),
                "source_row_number": validated.row_number,
            }
        )

    try:
        target_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = target_dir / (f"{source_path.stem}_processed_{run_uuid}.csv")

        pd.DataFrame(rows).to_csv(
            output_path,
            index=False,
            encoding="utf-8",
        )

        return output_path.resolve()

    except OSError as error:
        raise PipelineArtifactError(
            "Não foi possível gravar o arquivo processado."
        ) from error
