from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datalake.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from datalake.models.data_quality_issue_record import (
        DataQualityIssueRecord,
    )
    from datalake.models.ingestion_run import IngestionRun
    from datalake.models.patient import Patient


class StagedPatientRecord(TimestampMixin, Base):
    """Representação intermediária de uma linha do CSV."""

    __tablename__ = "patient_records"

    __table_args__ = (
        CheckConstraint(
            "source_row_number >= 2",
            name="source_row_after_header",
        ),
        CheckConstraint(
            """
            validation_status IN (
                'valid',
                'rejected'
            )
            """,
            name="validation_status_allowed",
        ),
        UniqueConstraint(
            "ingestion_run_id",
            "source_row_number",
            name="uq_patient_records_run_row",
        ),
        {"schema": "staging"},
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    ingestion_run_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "ingestion.ingestion_runs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    source_row_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    raw_record: Mapped[dict[str, str]] = mapped_column(
        JSONB,
        nullable=False,
    )

    normalized_external_code: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    normalized_birth_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    normalized_biological_sex: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    validation_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    patient_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "core.patients.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    ingestion_run: Mapped[IngestionRun] = relationship(
        back_populates="staged_records",
    )

    patient: Mapped[Patient | None] = relationship()

    quality_issues: Mapped[list[DataQualityIssueRecord]] = relationship(
        back_populates="staged_record",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )