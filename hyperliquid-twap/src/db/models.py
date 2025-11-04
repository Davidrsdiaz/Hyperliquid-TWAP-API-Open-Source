"""SQLAlchemy models for the Hyperliquid TWAP database."""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Index, Integer, Numeric, Text
from sqlalchemy.dialects.postgresql import TIMESTAMPTZ
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class TWAPStatus(Base):
    """TWAP status records from Hyperliquid parquet data."""

    __tablename__ = "twap_status"

    twap_id: Mapped[str] = mapped_column(Text, primary_key=True)
    wallet: Mapped[str] = mapped_column(Text, primary_key=True)
    ts: Mapped[datetime] = mapped_column(TIMESTAMPTZ, primary_key=True)
    asset: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    side: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    size_requested: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    size_executed: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    notional_executed: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    s3_object_key: Mapped[str] = mapped_column(Text, nullable=False)
    raw_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    inserted_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, default=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("twap_status_wallet_ts_idx", "wallet", "ts"),
        Index("twap_status_twap_id_idx", "twap_id"),
        Index("twap_status_asset_idx", "asset"),
    )


class ETLIngestLog(Base):
    """Log of processed S3 objects for idempotent ETL."""

    __tablename__ = "etl_s3_ingest_log"

    s3_object_key: Mapped[str] = mapped_column(Text, primary_key=True)
    last_modified: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False)
    rows_ingested: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ingested_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, default=datetime.utcnow, nullable=False
    )
