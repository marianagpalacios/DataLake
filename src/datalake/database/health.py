from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from datalake.database.engine import engine


def check_database_connection() -> bool:
    """Executa uma consulta mínima para verificar a conexão."""

    with engine.connect() as connection:
        result = connection.scalar(text("SELECT 1"))
        return result == 1


def main() -> None:
    try:
        if check_database_connection():
            print("Conexão com o PostgreSQL realizada com sucesso.")
    except SQLAlchemyError as error:
        print(
            "Não foi possível conectar ao PostgreSQL. "
            f"Tipo do erro: {type(error).__name__}"
        )
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
