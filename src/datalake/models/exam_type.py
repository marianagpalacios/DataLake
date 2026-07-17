from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, CheckConstraint, String, Text, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datalake.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from datalake.models.laboratory_exam import LaboratoryExam


class ExamType(TimestampMixin, Base):
    """Definição padronizada de um tipo de exame."""

    __tablename__ = "exam_types"

    __table_args__ = (
        CheckConstraint(
            """
            value_type IN (
                'numeric',
                'text',
                'boolean',
                'categorical'
            )
            """,
            name="value_type_allowed",
        ),
        {"schema": "core"},
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    default_unit: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    value_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )

    laboratory_exams: Mapped[list[LaboratoryExam]] = relationship(
        back_populates="exam_type",
    )