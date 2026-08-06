class ResourceNotFoundError(Exception):
    """Recurso solicitado não encontrado."""

    def __init__(
        self,
        resource: str,
        identifier: object,
    ) -> None:
        self.resource = resource
        self.identifier = identifier

        super().__init__(
            f"{resource} não encontrado: "
            f"{identifier}."
        )