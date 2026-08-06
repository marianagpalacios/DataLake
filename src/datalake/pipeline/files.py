from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from shutil import copy2

from datalake.pipeline.exceptions import SourceFileError


@dataclass(frozen=True)
class PreparedSourceFile:
    """Metadados e localização da cópia raw."""

    original_path: Path
    raw_path: Path
    sha256: str
    size_bytes: int


def calculate_sha256(file_path: str | Path) -> str:
    """Calcula SHA-256 sem carregar o arquivo inteiro na memória."""

    path = Path(file_path)

    digest = sha256()

    try:
        with path.open("rb") as source:
            while chunk := source.read(1024 * 1024):
                digest.update(chunk)

    except OSError as error:
        raise SourceFileError(
            f"Não foi possível calcular o hash de {path}."
        ) from error

    return digest.hexdigest()


def prepare_source_file(
    file_path: str | Path,
    raw_dir: str | Path = "data/raw",
) -> PreparedSourceFile:
    """Valida, identifica e preserva o arquivo na camada raw."""

    original_path = Path(file_path).resolve()

    if not original_path.exists():
        raise SourceFileError(
            f"Arquivo não encontrado: {original_path}."
        )

    if not original_path.is_file():
        raise SourceFileError(
            "O caminho informado não representa um arquivo: "
            f"{original_path}."
        )

    file_hash = calculate_sha256(original_path)
    size_bytes = original_path.stat().st_size

    target_dir = Path(raw_dir)
    target_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    raw_path = target_dir / (
        f"{file_hash[:12]}_{original_path.name}"
    )

    try:
        if not raw_path.exists():
            copy2(
                original_path,
                raw_path,
            )

    except OSError as error:
        raise SourceFileError(
            "Não foi possível preservar o arquivo "
            "na camada raw."
        ) from error

    return PreparedSourceFile(
        original_path=original_path,
        raw_path=raw_path.resolve(),
        sha256=file_hash,
        size_bytes=size_bytes,
    )