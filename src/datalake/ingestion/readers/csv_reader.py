from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError, ParserError

from datalake.ingestion.exceptions import CSVReadError


def read_csv_file(file_path: str | Path) -> pd.DataFrame:
    """Lê um arquivo CSV sem aplicar regras do domínio."""

    path = Path(file_path)

    if not path.exists():
        raise CSVReadError(
            f"Arquivo CSV não encontrado: {path}."
        )

    if not path.is_file():
        raise CSVReadError(
            f"O caminho informado não representa um arquivo: {path}."
        )

    try:
        return pd.read_csv(
            path,
            dtype=str,
            keep_default_na=False,
            skip_blank_lines=False,
            encoding="utf-8-sig",
            on_bad_lines="error",
        )
    except EmptyDataError as error:
        raise CSVReadError(
            "O arquivo CSV está vazio ou não possui cabeçalho."
        ) from error
    except ParserError as error:
        raise CSVReadError(
            "O arquivo CSV está malformado."
        ) from error
    except UnicodeDecodeError as error:
        raise CSVReadError(
            "O arquivo CSV não utiliza uma codificação UTF-8 válida."
        ) from error
    except OSError as error:
        raise CSVReadError(
            f"Não foi possível acessar o arquivo CSV: {error}."
        ) from error