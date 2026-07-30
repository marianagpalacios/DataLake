import argparse
import sys
from pathlib import Path

from datalake.ingestion.exceptions import (
    CSVReadError,
    PatientIngestionError,
    PatientValidationError,
)
from datalake.ingestion.services import ingest_patients_csv


def build_parser() -> argparse.ArgumentParser:
    """Cria o interpretador de argumentos da linha de comando."""

    parser = argparse.ArgumentParser(
        prog="datalake-ingest-patients",
        description=(
            "Importa pacientes sintéticos de um arquivo CSV "
            "para o PostgreSQL."
        ),
    )

    parser.add_argument(
        "file_path",
        type=Path,
        help="Caminho do arquivo CSV de pacientes.",
    )

    return parser


def main() -> None:
    parser = build_parser()
    arguments = parser.parse_args()

    try:
        result = ingest_patients_csv(
            arguments.file_path
        )
    except (
        CSVReadError,
        PatientValidationError,
        PatientIngestionError,
    ) as error:
        print(
            f"Erro durante a ingestão:\n{error}",
            file=sys.stderr,
        )

        raise SystemExit(1) from error

    print("Ingestão concluída.")
    print()
    print(f"Arquivo: {result.source_file}")
    print(
        "Registros recebidos: "
        f"{result.received_count}"
    )
    print(
        "Registros inseridos: "
        f"{result.inserted_count}"
    )
    print(
        "Registros já existentes: "
        f"{result.existing_count}"
    )
    print(f"Avisos: {len(result.warnings)}")

    for warning in result.warnings:
        print(f"- {warning}")


if __name__ == "__main__":
    main()