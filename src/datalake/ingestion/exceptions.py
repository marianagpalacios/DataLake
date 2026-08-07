class CSVReadError(Exception):
    """Erro ao localizar ou interpretar um arquivo CSV."""


class PatientValidationError(Exception):
    """Erro causado por dados de pacientes incompatíveis com o contrato."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = tuple(errors)

        details = "\n".join(f"- {message}" for message in self.errors)

        super().__init__(f"O arquivo de pacientes possui erros:\n{details}")


class PatientIngestionError(Exception):
    """Erro ocorrido durante a persistência dos pacientes."""
