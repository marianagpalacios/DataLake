from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datalake.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from datalake.models.source_file import SourceFile
    from datalake.models.staged_patient_record import StagedPatientRecord


class IngestionRun(TimestampMixin, Base):
    """Tentativa rastreável de processamento de um arquivo."""

    __tablename__ = "ingestion_runs"

    __table_args__ = (
        CheckConstraint(
            """
            status IN (
                'running',
                'completed',
                'completed_with_rejections',
                'failed',
                'skipped_duplicate'
            )
            """,
            name="status_allowed",
        ),
        CheckConstraint(
            """
            received_count >= 0
            AND valid_count >= 0
            AND rejected_count >= 0
            AND inserted_count >= 0
            AND existing_count >= 0
            """,
            name="counts_non_negative",
        ),
        CheckConstraint(
            "received_count = valid_count + rejected_count",
            name="received_matches_quality_counts",
        ),
        CheckConstraint(
            "valid_count = inserted_count + existing_count",
            name="valid_matches_load_counts",
        ),
        CheckConstraint(
            """
            acceptance_rate >= 0
            AND acceptance_rate <= 100
            """,
            name="acceptance_rate_range",
        ),
        CheckConstraint(
            """
            (
                status = 'running'
                AND finished_at IS NULL
            )
            OR
            (
                status <> 'running'
                AND finished_at IS NOT NULL
            )
            """,
            name="finished_at_matches_status",
        ),
        {"schema": "ingestion"},
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    run_uuid: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        default=uuid4,
        nullable=False,
        unique=True,
    )

    source_file_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "ingestion.source_files.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    duplicate_of_run_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "ingestion.ingestion_runs.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="running",
        server_default="running",
    )

    pipeline_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="patient_csv",
        server_default="patient_csv",
    )

    pipeline_version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    received_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )

    valid_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )

    rejected_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )

    inserted_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )

    existing_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )

    acceptance_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default=text("0"),
    )

    processed_file_path: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    rejection_file_path: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    source_file: Mapped[SourceFile] = relationship(
        back_populates="ingestion_runs",
    )

    duplicate_of: Mapped[IngestionRun | None] = relationship(
        "IngestionRun",
        remote_side="IngestionRun.id",
        foreign_keys=[duplicate_of_run_id],
        back_populates="duplicate_attempts",
    )

    duplicate_attempts: Mapped[list[IngestionRun]] = relationship(
        "IngestionRun",
        foreign_keys=[duplicate_of_run_id],
        back_populates="duplicate_of",
    )

    staged_records: Mapped[list[StagedPatientRecord]] = relationship(
        back_populates="ingestion_run",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
