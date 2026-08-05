from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from datalake.quality.exceptions import QualityReportError
from datalake.quality.models import RejectedPatientRecord


def write_rejected_patient_report(
    rejected_records: tuple[RejectedPatientRecord, ...],
    source_file: str | Path,
    output_dir: str | Path = "data/rejected",
) -> Path | None:
    """Grava os registros rejeitados em um CSV local."""

    if not rejected_records:
        return None

    source_path = Path(source_file)
    target_dir = Path(output_dir)

    try:
        target_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        timestamp = datetime.now(
            timezone.utc
        ).strftime(
            "%Y%m%dT%H%M%S%fZ"
        )

        report_path = target_dir / (
            f"{source_path.stem}_rejected_"
            f"{timestamp}.csv"
        )

        rows: list[dict[str, object]] = []

        for rejected in rejected_records:
            row: dict[str, object] = dict(
                rejected.raw_record
            )

            row["source_row_number"] = (
                rejected.row_number
            )

            row["error_codes"] = "|".join(
                issue.code
                for issue in rejected.issues
            )

            row["error_fields"] = "|".join(
                issue.field
                for issue in rejected.issues
            )

            row["error_messages"] = " | ".join(
                issue.message
                for issue in rejected.issues
            )

            rows.append(row)

        pd.DataFrame(rows).to_csv(
            report_path,
            index=False,
            encoding="utf-8",
        )

        return report_path.resolve()

    except OSError as error:
        raise QualityReportError(
            "Não foi possível gravar o relatório "
            "de registros rejeitados."
        ) from error