from dataclasses import dataclass
from datetime import date

import pandas as pd

from datalake.ingestion.exceptions import PatientValidationError


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


@dataclass(frozen=True)
class PatientValidationResult:
    """Dados normalizados e avisos não bloqueantes."""

    dataframe: pd.DataFrame
    warnings: tuple[str, ...]


def _csv_rows(indexes: pd.Index) -> str:
    """Converte índices do DataFrame em números de linha do CSV."""

    return ", ".join(
        str(int(index) + 2)
        for index in indexes
    )


def validate_patient_dataframe(
    dataframe: pd.DataFrame,
) -> PatientValidationResult:
    """Valida e normaliza um DataFrame de pacientes."""

    missing_columns = REQUIRED_PATIENT_COLUMNS.difference(
        dataframe.columns
    )

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))

        raise PatientValidationError(
            [
                "Colunas obrigatórias ausentes: "
                f"{missing}."
            ]
        )

    if dataframe.empty:
        raise PatientValidationError(
            ["O arquivo não possui registros de pacientes."]
        )

    normalized = dataframe[
        [
            "external_code",
            "birth_date",
            "biological_sex",
        ]
    ].copy()

    errors: list[str] = []
    warnings: list[str] = []

    extra_columns = set(dataframe.columns).difference(
        REQUIRED_PATIENT_COLUMNS
    )

    if extra_columns:
        extras = ", ".join(sorted(extra_columns))

        warnings.append(
            "Colunas adicionais foram ignoradas: "
            f"{extras}."
        )

    original_codes = normalized["external_code"].astype(str)
    normalized_codes = original_codes.str.strip()

    changed_codes = original_codes.ne(normalized_codes)

    if changed_codes.any():
        warnings.append(
            "Espaços externos foram removidos de "
            "`external_code` nas linhas "
            f"{_csv_rows(normalized.index[changed_codes])}."
        )

    normalized["external_code"] = normalized_codes

    blank_codes = normalized["external_code"].eq("")

    if blank_codes.any():
        errors.append(
            "Código externo vazio nas linhas "
            f"{_csv_rows(normalized.index[blank_codes])}."
        )

    nonempty_codes = normalized.loc[
        ~blank_codes,
        "external_code",
    ]

    duplicate_codes = nonempty_codes.duplicated(
        keep=False
    )

    if duplicate_codes.any():
        errors.append(
            "Códigos externos duplicados nas linhas "
            f"{_csv_rows(nonempty_codes.index[duplicate_codes])}."
        )

    original_dates = normalized["birth_date"].astype(str)
    normalized_dates = original_dates.str.strip()

    changed_dates = original_dates.ne(normalized_dates)

    if changed_dates.any():
        warnings.append(
            "Espaços externos foram removidos de "
            "`birth_date` nas linhas "
            f"{_csv_rows(normalized.index[changed_dates])}."
        )

    parsed_dates = pd.to_datetime(
        normalized_dates.where(
            normalized_dates.ne(""),
            pd.NA,
        ),
        format="%Y-%m-%d",
        errors="coerce",
    )

    invalid_dates = (
        normalized_dates.ne("")
        & parsed_dates.isna()
    )

    if invalid_dates.any():
        errors.append(
            "Datas inválidas nas linhas "
            f"{_csv_rows(normalized.index[invalid_dates])}. "
            "Use o formato AAAA-MM-DD."
        )

    original_sex = normalized["biological_sex"].astype(str)
    stripped_sex = original_sex.str.strip()
    normalized_sex = stripped_sex.str.lower()

    changed_sex = original_sex.ne(normalized_sex)

    if changed_sex.any():
        warnings.append(
            "Valores de `biological_sex` foram normalizados "
            "nas linhas "
            f"{_csv_rows(normalized.index[changed_sex])}."
        )

    invalid_sex = (
        normalized_sex.ne("")
        & ~normalized_sex.isin(ALLOWED_BIOLOGICAL_SEX)
    )

    if invalid_sex.any():
        errors.append(
            "Valores inválidos para `biological_sex` "
            "nas linhas "
            f"{_csv_rows(normalized.index[invalid_sex])}."
        )

    if errors:
        raise PatientValidationError(errors)

    normalized["birth_date"] = [
        parsed_value.date()
        if original_value
        else None
        for original_value, parsed_value
        in zip(
            normalized_dates.tolist(),
            parsed_dates.tolist(),
        )
    ]

    normalized["biological_sex"] = [
        value if value else None
        for value in normalized_sex.tolist()
    ]

    return PatientValidationResult(
        dataframe=normalized.reset_index(drop=True),
        warnings=tuple(warnings),
    )