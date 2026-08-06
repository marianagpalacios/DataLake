from collections import Counter
from datetime import date, datetime

import pandas as pd

from datalake.ingestion.exceptions import (
    PatientValidationError,
)
from datalake.quality.models import (
    DataQualityIssue,
    PatientValidationResult,
    RejectedPatientRecord,
    ValidatedPatientRecord,
)


REQUIRED_PATIENT_COLUMNS = frozenset(
    {
        "external_code",
        "birth_date",
        "biological_sex",
    }
)

ALLOWED_BIOLOGICAL_SEX = frozenset(
    {
        "female",
        "male",
        "intersex",
        "unknown",
        "not_informed",
    }
)


def _as_text(value: object) -> str:
    """Converte um valor do DataFrame em texto seguro."""

    if value is None or pd.isna(value):
        return ""

    return str(value)


def _parse_birth_date(value: str) -> date:
    """Converte uma data estritamente em AAAA-MM-DD."""

    parsed = datetime.strptime(
        value,
        "%Y-%m-%d",
    ).date()

    if parsed.isoformat() != value:
        raise ValueError(
            "Formato de data não canônico."
        )

    return parsed


def validate_patient_dataframe(
    dataframe: pd.DataFrame,
    today: date | None = None,
) -> PatientValidationResult:
    """Separa registros válidos e rejeitados."""

    missing_columns = (
        REQUIRED_PATIENT_COLUMNS.difference(
            dataframe.columns
        )
    )

    if missing_columns:
        missing = ", ".join(
            sorted(missing_columns)
        )

        raise PatientValidationError(
            [
                "Colunas obrigatórias ausentes: "
                f"{missing}."
            ]
        )

    if dataframe.empty:
        raise PatientValidationError(
            [
                "O arquivo não possui registros "
                "de pacientes."
            ]
        )

    reference_date = today or date.today()
    warnings: list[str] = []

    extra_columns = set(
        dataframe.columns
    ).difference(
        REQUIRED_PATIENT_COLUMNS
    )

    if extra_columns:
        extras = ", ".join(
            sorted(extra_columns)
        )

        warnings.append(
            "Colunas adicionais foram preservadas "
            "somente no relatório de rejeições e "
            f"ignoradas na carga: {extras}."
        )

    normalized_codes = [
        _as_text(value).strip()
        for value
        in dataframe["external_code"].tolist()
    ]

    code_counts = Counter(
        code
        for code in normalized_codes
        if code
    )

    valid_records: list[ValidatedPatientRecord] = []

    rejected_records: list[
        RejectedPatientRecord
    ] = []

    for position, (_, row) in enumerate(
        dataframe.iterrows(),
        start=2,
    ):
        raw_record = {
            column: _as_text(row[column])
            for column in dataframe.columns
        }

        issues: list[DataQualityIssue] = []

        raw_code = raw_record["external_code"]
        external_code = raw_code.strip()

        if raw_code != external_code:
            warnings.append(
                "Espaços externos foram removidos "
                "de `external_code` na linha "
                f"{position}."
            )

        if not external_code:
            issues.append(
                DataQualityIssue(
                    row_number=position,
                    field="external_code",
                    code="required_value_missing",
                    message=(
                        "O código externo é "
                        "obrigatório."
                    ),
                    raw_value=raw_code,
                )
            )

        elif code_counts[external_code] > 1:
            issues.append(
                DataQualityIssue(
                    row_number=position,
                    field="external_code",
                    code="duplicate_in_file",
                    message=(
                        "O código externo está "
                        "duplicado dentro do arquivo."
                    ),
                    raw_value=raw_code,
                )
            )

        raw_birth_date = raw_record[
            "birth_date"
        ]

        normalized_birth_date = (
            raw_birth_date.strip()
        )

        birth_date_value: date | None = None

        if (
            raw_birth_date
            != normalized_birth_date
        ):
            warnings.append(
                "Espaços externos foram removidos "
                "de `birth_date` na linha "
                f"{position}."
            )

        if normalized_birth_date:
            try:
                birth_date_value = (
                    _parse_birth_date(
                        normalized_birth_date
                    )
                )

            except ValueError:
                issues.append(
                    DataQualityIssue(
                        row_number=position,
                        field="birth_date",
                        code=(
                            "invalid_date_format"
                        ),
                        message=(
                            "A data deve usar o "
                            "formato AAAA-MM-DD."
                        ),
                        raw_value=raw_birth_date,
                    )
                )

            else:
                if (
                    birth_date_value
                    > reference_date
                ):
                    issues.append(
                        DataQualityIssue(
                            row_number=position,
                            field="birth_date",
                            code=(
                                "future_birth_date"
                            ),
                            message=(
                                "A data de nascimento "
                                "não pode estar no "
                                "futuro."
                            ),
                            raw_value=(
                                raw_birth_date
                            ),
                        )
                    )

        raw_sex = raw_record[
            "biological_sex"
        ]

        stripped_sex = raw_sex.strip()
        biological_sex = (
            stripped_sex.lower()
        )

        if raw_sex != biological_sex:
            warnings.append(
                "O valor de `biological_sex` "
                "foi normalizado na linha "
                f"{position}."
            )

        biological_sex_value = (
            biological_sex
            if biological_sex
            else None
        )

        if (
            biological_sex_value is not None
            and biological_sex_value
            not in ALLOWED_BIOLOGICAL_SEX
        ):
            issues.append(
                DataQualityIssue(
                    row_number=position,
                    field="biological_sex",
                    code=(
                        "invalid_biological_sex"
                    ),
                    message=(
                        "O valor de sexo biológico "
                        "não pertence à lista "
                        "permitida."
                    ),
                    raw_value=raw_sex,
                )
            )

        if issues:
            rejected_records.append(
                RejectedPatientRecord(
                    row_number=position,
                    raw_record=raw_record,
                    issues=tuple(issues),
                )
            )

            continue

        valid_records.append(
            ValidatedPatientRecord(
                row_number=position,
                raw_record=raw_record,
                normalized_record={
                    "external_code": external_code,
                    "birth_date": birth_date_value,
                    "biological_sex": biological_sex_value,
                },
            )
        )

    return PatientValidationResult(
        valid_records=tuple(valid_records),
        rejected_records=tuple(
            rejected_records
        ),
        warnings=tuple(warnings),
    )
