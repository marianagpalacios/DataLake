from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class DataQualityIssue:
    """Problema de qualidade encontrado em uma linha."""

    row_number: int
    field: str
    code: str
    message: str
    raw_value: str | None


@dataclass(frozen=True)
class RejectedPatientRecord:
    """Registro rejeitado e seus respectivos problemas."""

    row_number: int
    raw_record: Mapping[str, str]
    issues: tuple[DataQualityIssue, ...]


@dataclass(frozen=True)
class PatientValidationResult:
    """Resultado da validação linha a linha."""

    valid_records: tuple[dict[str, object], ...]
    rejected_records: tuple[RejectedPatientRecord, ...]
    warnings: tuple[str, ...]

    @property
    def received_count(self) -> int:
        return (
            len(self.valid_records)
            + len(self.rejected_records)
        )

    @property
    def valid_count(self) -> int:
        return len(self.valid_records)

    @property
    def rejected_count(self) -> int:
        return len(self.rejected_records)

    @property
    def acceptance_rate(self) -> float:
        if self.received_count == 0:
            return 0.0

        return round(
            self.valid_count
            / self.received_count
            * 100,
            2,
        )