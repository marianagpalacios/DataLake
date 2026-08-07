from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datalake.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from datalake.models.data_source import DataSource
    from datalake.models.ingestion_run import IngestionRun


class SourceFile(TimestampMixin, Base):
    """Arquivo físico recebido por uma fonte de dados."""

    __tablename__ = "source_files"

    __table_args__ = (
        CheckConstraint(
            "size_bytes >= 0",
            name="size_bytes_non_negative",
        ),
        UniqueConstraint(
            "data_source_id",
            "sha256",
            name="uq_source_files_source_sha256",
        ),
        {"schema": "ingestion"},
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
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

    sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    original_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    stored_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    data_source: Mapped[DataSource] = relationship(
        back_populates="source_files",
    )

    ingestion_runs: Mapped[list[IngestionRun]] = relationship(
        back_populates="source_file",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
