class SourceFileError(Exception):
    """Erro ao inspecionar ou preservar o arquivo de origem."""


class PipelineArtifactError(Exception):
    """Erro ao gerar um artefato processado."""


class PatientETLError(Exception):
    """Erro ocorrido durante o pipeline ETL de pacientes."""