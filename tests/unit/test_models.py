import datalake.models
from datalake.database.base import Base


def test_expected_tables_are_registered() -> None:
    expected_tables = {
        "ingestion.data_sources",
        "core.patients",
        "core.exam_types",
        "core.biological_samples",
        "core.laboratory_exams",
        "core.exam_results",
    }

    assert set(Base.metadata.tables.keys()) == expected_tables