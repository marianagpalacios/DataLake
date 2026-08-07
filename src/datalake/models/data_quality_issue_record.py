from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datalake.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from datalake.models.staged_patient_record import StagedPatientRecord


class DataQualityIssueRecord(TimestampMixin, Base):
    """Problema de qualidade persistido no PostgreSQL."""

    __tablename__ = "data_quality_issues"

    __table_args__ = ({"schema": "quality"},)

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    staged_record_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "staging.patient_records.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    field: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    raw_value: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    staged_record: Mapped[StagedPatientRecord] = relationship(
        back_populates="quality_issues",
    )
