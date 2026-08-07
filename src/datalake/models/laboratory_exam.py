from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datalake.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from datalake.models.biological_sample import BiologicalSample
    from datalake.models.data_source import DataSource
    from datalake.models.exam_result import ExamResult
    from datalake.models.exam_type import ExamType
    from datalake.models.patient import Patient


class LaboratoryExam(TimestampMixin, Base):
    """Execução concreta de um exame laboratorial."""

    __tablename__ = "laboratory_exams"

    __table_args__ = (
        CheckConstraint(
            """
            status IN (
                'registered',
                'processing',
                'completed',
                'cancelled'
            )
            """,
            name="status_allowed",
        ),
        CheckConstraint(
            """
            performed_at IS NULL
            OR requested_at IS NULL
            OR performed_at >= requested_at
            """,
            name="performed_after_requested",
        ),
        UniqueConstraint(
            "data_source_id",
            "external_exam_code",
            name="uq_laboratory_exams_source_external_code",
        ),
        {"schema": "core"},
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    patient_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "core.patients.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    exam_type_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "core.exam_types.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    sample_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "core.biological_samples.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    data_source_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "ingestion.data_sources.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    external_exam_code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="registered",
        server_default="registered",
    )

    requested_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    performed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    patient: Mapped[Patient] = relationship(
        back_populates="laboratory_exams",
    )

    exam_type: Mapped[ExamType] = relationship(
        back_populates="laboratory_exams",
    )

    sample: Mapped[BiologicalSample | None] = relationship(
        back_populates="laboratory_exams",
    )

    data_source: Mapped[DataSource] = relationship(
        back_populates="laboratory_exams",
    )

    results: Mapped[list[ExamResult]] = relationship(
        back_populates="laboratory_exam",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
