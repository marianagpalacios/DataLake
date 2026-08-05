import argparse
import sys
from pathlib import Path

from datalake.ingestion.exceptions import (
    CSVReadError,
    PatientIngestionError,
    PatientValidationError,
)
from datalake.ingestion.services import (
    ingest_patients_csv,
)
from datalake.quality.exceptions import (
    QualityReportError,
)


def build_parser() -> argparse.ArgumentParser:
    """Cria os argumentos da linha de comando."""

    parser = argparse.ArgumentParser(
        prog="datalake-ingest-patients",
        description=(
            "Importa pacientes sintéticos de "
            "um CSV, separando registros "
            "válidos e rejeitados."
        ),
    )

    parser.add_argument(
        "file_path",
        type=Path,
        help=(
            "Caminho do arquivo CSV de "
            "pacientes."
        ),
    )

    parser.add_argument(
        "--rejected-dir",
        type=Path,
        default=Path("data/rejected"),
        help=(
            "Pasta local para o relatório "
            "de registros rejeitados."
        ),
    )

    return parser


def main() -> None:
    parser = build_parser()
    arguments = parser.parse_args()

    try:
        result = ingest_patients_csv(
            arguments.file_path,
            rejection_output_dir=(
                arguments.rejected_dir
            ),
        )

    except (
        CSVReadError,
        PatientValidationError,
        PatientIngestionError,
        QualityReportError,
    ) as error:
        print(
            f"Erro durante a ingestão:\n"
            f"{error}",
            file=sys.stderr,
        )

        raise SystemExit(1) from error

    print("Ingestão concluída.")
    print()

    print(f"Status: {result.status}")
    print(f"Arquivo: {result.source_file}")

    print(
        "Registros recebidos: "
        f"{result.received_count}"
    )

    print(
        "Registros válidos: "
        f"{result.valid_count}"
    )

    print(
        "Registros rejeitados: "
        f"{result.rejected_count}"
    )

    print(
        "Registros inseridos: "
        f"{result.inserted_count}"
    )

    print(
        "Registros já existentes: "
        f"{result.existing_count}"
    )

    print(
        "Taxa de aceitação: "
        f"{result.acceptance_rate:.2f}%"
    )

    print(
        f"Avisos: {len(result.warnings)}"
    )

    if result.rejection_file is not None:
        print(
            "Relatório de rejeições: "
            f"{result.rejection_file}"
        )

    for warning in result.warnings:
        print(f"- {warning}")


if __name__ == "__main__":
    main()