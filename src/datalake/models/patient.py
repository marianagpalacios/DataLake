from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, CheckConstraint, Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datalake.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from datalake.models.biological_sample import BiologicalSample
    from datalake.models.laboratory_exam import LaboratoryExam


class Patient(TimestampMixin, Base):
    """Paciente fictício ou pseudonimizado."""

    __tablename__ = "patients"

    __table_args__ = (
        CheckConstraint(
            """
            biological_sex IS NULL
            OR biological_sex IN (
                'female',
                'male',
                'intersex',
                'unknown',
                'not_informed'
            )
            """,
            name="biological_sex_allowed",
        ),
        {"schema": "core"},
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    external_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    birth_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    biological_sex: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    samples: Mapped[list[BiologicalSample]] = relationship(
        back_populates="patient",
    )

    laboratory_exams: Mapped[list[LaboratoryExam]] = relationship(
        back_populates="patient",
    )
