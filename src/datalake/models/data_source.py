from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, CheckConstraint, String, Text, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datalake.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from datalake.models.laboratory_exam import LaboratoryExam
    from datalake.models.source_file import SourceFile


class DataSource(TimestampMixin, Base):
    """Sistema, arquivo ou instituição que originou os dados."""

    __tablename__ = "data_sources"

    __table_args__ = (
        CheckConstraint(
            """
            source_type IN (
                'csv',
                'json',
                'api',
                'database',
                'spreadsheet',
                'synthetic',
                'public'
            )
            """,
            name="source_type_allowed",
        ),
        {"schema": "ingestion"},
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        unique=True,
    )

    source_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )

    laboratory_exams: Mapped[list[LaboratoryExam]] = relationship(
        back_populates="data_source",
    )

    source_files: Mapped[list[SourceFile]] = relationship(
        back_populates="data_source",
    )
