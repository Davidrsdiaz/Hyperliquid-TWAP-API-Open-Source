"""Pydantic models for API request/response validation."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ExecutedData(BaseModel):
    """Executed size and notional data."""

    size: Optional[str] = Field(None, description="Executed size")
    notional: Optional[str] = Field(None, description="Executed notional value")


class TWAPData(BaseModel):
    """TWAP data for a single TWAP ID."""

    twap_id: str = Field(..., description="TWAP identifier")
    asset: Optional[str] = Field(None, description="Asset/coin")
    side: Optional[str] = Field(None, description="Buy/Sell side")
    status: Optional[str] = Field(None, description="TWAP status")
    duration_minutes: Optional[int] = Field(None, description="TWAP duration in minutes")
    latest_ts: datetime = Field(..., description="Most recent timestamp for this TWAP")
    executed: ExecutedData = Field(..., description="Executed amounts")
    raw: Dict[str, Any] = Field({}, description="Raw parquet row data")


class TWAPsResponse(BaseModel):
    """Response model for GET /api/v1/twaps."""

    wallet: str = Field(..., description="Wallet address")
    start: datetime = Field(..., description="Start of query time range")
    end: datetime = Field(..., description="End of query time range")
    twaps: List[TWAPData] = Field(default_factory=list, description="List of TWAPs")


class TWAPRow(BaseModel):
    """Single TWAP status row."""

    wallet: str
    ts: datetime
    asset: Optional[str] = None
    side: Optional[str] = None
    size_requested: Optional[str] = None
    size_executed: Optional[str] = None
    notional_executed: Optional[str] = None
    status: Optional[str] = None
    duration_minutes: Optional[int] = None
    raw: Dict[str, Any] = Field(default_factory=dict)


class TWAPDetailResponse(BaseModel):
    """Response model for GET /api/v1/twaps/{twap_id}."""

    twap_id: str = Field(..., description="TWAP identifier")
    rows: List[TWAPRow] = Field(default_factory=list, description="All rows for this TWAP")


class HealthResponse(BaseModel):
    """Response model for GET /healthz."""

    status: str = Field(..., description="Service health status")
    database: str = Field(..., description="Database connection status")
    last_ingested_object: Optional[str] = Field(None, description="Most recently ingested S3 object")
    last_ingested_at: Optional[datetime] = Field(None, description="When the last object was ingested")
