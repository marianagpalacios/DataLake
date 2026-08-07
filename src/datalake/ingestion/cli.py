import argparse
import sys
from pathlib import Path

from datalake.ingestion.exceptions import (
    CSVReadError,
    PatientIngestionError,
    PatientValidationError,
)
from datalake.pipeline import run_patient_etl
from datalake.pipeline.exceptions import (
    PatientETLError,
    PipelineArtifactError,
    SourceFileError,
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
        help=("Caminho do arquivo CSV de pacientes."),
    )

    parser.add_argument(
        "--source-name",
        default="patient_csv_cli",
        help="Nome lógico da fonte de dados.",
    )

    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=Path("data/raw"),
        help="Pasta da camada raw.",
    )

    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=Path("data/processed"),
        help="Pasta dos dados processados.",
    )

    parser.add_argument(
        "--rejected-dir",
        type=Path,
        default=Path("data/rejected"),
        help="Pasta dos relatórios de rejeição.",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=("Reprocessa o arquivo mesmo quando seu hash já tiver sido concluído."),
    )

    return parser


def main() -> None:
    parser = build_parser()
    arguments = parser.parse_args()

    try:
        result = run_patient_etl(
            file_path=arguments.file_path,
            source_name=arguments.source_name,
            raw_dir=arguments.raw_dir,
            processed_dir=arguments.processed_dir,
            rejected_dir=arguments.rejected_dir,
            force=arguments.force,
        )

    except (
        CSVReadError,
        PatientValidationError,
        PatientIngestionError,
        QualityReportError,
        SourceFileError,
        PipelineArtifactError,
        PatientETLError,
    ) as error:
        print(
            f"Erro durante a ingestão:\n{error}",
            file=sys.stderr,
        )

        raise SystemExit(1) from error

    print("Ingestão concluída.")
    print()

    print(f"Execução: {result.run_uuid}")
    print(f"Status: {result.status}")
    print(f"Arquivo: {result.source_file}")
    print(f"SHA-256: {result.source_sha256}")
    print(f"Camada raw: {result.raw_file}")

    if result.processed_file is not None:
        print(f"Arquivo processado: {result.processed_file}")

    if result.rejection_file is not None:
        print(f"Relatório de rejeições: {result.rejection_file}")

    if result.duplicate_of_run_uuid is not None:
        print(f"Execução original: {result.duplicate_of_run_uuid}")

    print(f"Registros recebidos: {result.received_count}")

    print(f"Registros válidos: {result.valid_count}")

    print(f"Registros rejeitados: {result.rejected_count}")

    print(f"Registros inseridos: {result.inserted_count}")

    print(f"Registros já existentes: {result.existing_count}")

    print(f"Taxa de aceitação: {result.acceptance_rate:.2f}%")

    print(f"Avisos: {len(result.warnings)}")

    for warning in result.warnings:
        print(f"- {warning}")


if __name__ == "__main__":
    main()
