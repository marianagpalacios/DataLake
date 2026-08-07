from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datalake.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from datalake.models.laboratory_exam import LaboratoryExam


class ExamResult(TimestampMixin, Base):
    """Componente de resultado produzido por um exame."""

    __tablename__ = "exam_results"

    __table_args__ = (
        CheckConstraint(
            """
            (
                result_value_numeric IS NOT NULL
                AND result_value_text IS NULL
            )
            OR
            (
                result_value_numeric IS NULL
                AND result_value_text IS NOT NULL
            )
            """,
            name="exactly_one_result_value",
        ),
        UniqueConstraint(
            "laboratory_exam_id",
            "result_code",
            name="uq_exam_results_exam_result_code",
        ),
        {"schema": "core"},
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    laboratory_exam_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "core.laboratory_exams.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    result_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    result_value_numeric: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 6),
        nullable=True,
    )

    result_value_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    unit: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    reference_range: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    is_abnormal: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    laboratory_exam: Mapped[LaboratoryExam] = relationship(
        back_populates="results",
    )
