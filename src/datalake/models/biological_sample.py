from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datalake.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from datalake.models.laboratory_exam import LaboratoryExam
    from datalake.models.patient import Patient


class BiologicalSample(TimestampMixin, Base):
    """Material biológico coletado de um paciente."""

    __tablename__ = "biological_samples"

    __table_args__ = (
        CheckConstraint(
            """
            sample_type IN (
                'blood',
                'serum',
                'plasma',
                'saliva',
                'urine',
                'tissue',
                'other'
            )
            """,
            name="sample_type_allowed",
        ),
        CheckConstraint(
            """
            received_at IS NULL
            OR received_at >= collected_at
            """,
            name="received_after_collection",
        ),
        {"schema": "core"},
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    sample_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
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

    sample_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    received_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    patient: Mapped[Patient] = relationship(
        back_populates="samples",
    )

    laboratory_exams: Mapped[list[LaboratoryExam]] = relationship(
        back_populates="sample",
    )