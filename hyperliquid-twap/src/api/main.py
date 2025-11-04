"""FastAPI application main module."""

import os
from datetime import datetime
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import ETLIngestLog, TWAPStatus
from .database import get_db
from .metrics import metrics, metrics_middleware
from .models import (
    ExecutedData,
    HealthResponse,
    TWAPData,
    TWAPDetailResponse,
    TWAPRow,
    TWAPsResponse,
)

app = FastAPI(
    title="Hyperliquid TWAP Data Service",
    description="API for querying Hyperliquid TWAP data from Artemis S3 bucket",
    version="0.1.0"
)

# Configure CORS
# Allow origins can be configured via CORS_ORIGINS environment variable
# Format: comma-separated list, e.g., "http://localhost:3000,https://app.example.com"
# Default: Allow all origins (use specific origins in production)
cors_origins = os.getenv("CORS_ORIGINS", "*")
if cors_origins == "*":
    allowed_origins = ["*"]
else:
    allowed_origins = [origin.strip() for origin in cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add metrics middleware
app.middleware("http")(metrics_middleware)


@app.get("/api/v1/twaps", response_model=TWAPsResponse)
async def get_twaps(
    wallet: str = Query(..., description="Wallet address"),
    start: datetime = Query(..., description="Start timestamp (ISO8601)"),
    end: datetime = Query(..., description="End timestamp (ISO8601)"),
    asset: Optional[str] = Query(None, description="Filter by asset/coin"),
    latest_per_twap: bool = Query(True, description="Return only latest row per TWAP ID"),
    limit: int = Query(500, ge=1, le=5000, description="Maximum number of TWAPs to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination (number of TWAPs to skip)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Query TWAPs by wallet and time range with pagination support.
    
    Returns TWAPs grouped by twap_id. If latest_per_twap=true, returns only
    the most recent row per TWAP ID.
    
    Pagination:
    - Use `limit` to control page size (default 500, max 5000)
    - Use `offset` to skip TWAPs for pagination (default 0)
    - Example: offset=0&limit=100 for page 1, offset=100&limit=100 for page 2
    """
    # Build query
    query = select(TWAPStatus).where(
        TWAPStatus.wallet == wallet,
        TWAPStatus.ts >= start,
        TWAPStatus.ts <= end
    )
    
    # Add asset filter if provided
    if asset:
        query = query.where(TWAPStatus.asset == asset)
    
    # Order by twap_id and timestamp (descending for latest)
    query = query.order_by(TWAPStatus.twap_id, TWAPStatus.ts.desc())
    
    # Execute query
    result = await db.execute(query)
    rows = result.scalars().all()
    
    # Group by twap_id
    twap_groups = {}
    for row in rows:
        if row.twap_id not in twap_groups:
            twap_groups[row.twap_id] = []
        twap_groups[row.twap_id].append(row)
    
    # Build response with pagination
    twaps = []
    twap_ids = list(twap_groups.keys())
    
    # Apply offset and limit to twap_ids
    paginated_twap_ids = twap_ids[offset:offset + limit]
    
    for twap_id in paginated_twap_ids:
        twap_rows = twap_groups[twap_id]
        
        # If latest_per_twap, use only the first row (already sorted desc by ts)
        if latest_per_twap:
            latest_row = twap_rows[0]
            twap_data = TWAPData(
                twap_id=twap_id,
                asset=latest_row.asset,
                side=latest_row.side,
                status=latest_row.status,
                duration_minutes=latest_row.duration_minutes,
                latest_ts=latest_row.ts,
                executed=ExecutedData(
                    size=str(latest_row.size_executed) if latest_row.size_executed is not None else None,
                    notional=str(latest_row.notional_executed) if latest_row.notional_executed is not None else None
                ),
                raw=latest_row.raw_payload or {}
            )
            twaps.append(twap_data)
        else:
            # Return data from latest row but include all rows in raw
            latest_row = twap_rows[0]
            twap_data = TWAPData(
                twap_id=twap_id,
                asset=latest_row.asset,
                side=latest_row.side,
                status=latest_row.status,
                duration_minutes=latest_row.duration_minutes,
                latest_ts=latest_row.ts,
                executed=ExecutedData(
                    size=str(latest_row.size_executed) if latest_row.size_executed is not None else None,
                    notional=str(latest_row.notional_executed) if latest_row.notional_executed is not None else None
                ),
                raw={
                    "latest": latest_row.raw_payload or {},
                    "all_rows": [r.raw_payload for r in twap_rows if r.raw_payload]
                }
            )
            twaps.append(twap_data)
    
    return TWAPsResponse(
        wallet=wallet,
        start=start,
        end=end,
        twaps=twaps
    )


@app.get("/api/v1/twaps/{twap_id}", response_model=TWAPDetailResponse)
async def get_twap_by_id(
    twap_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all rows for a specific TWAP ID.
    
    Returns complete history of status updates for the TWAP.
    """
    # Query all rows for this TWAP ID
    query = select(TWAPStatus).where(
        TWAPStatus.twap_id == twap_id
    ).order_by(TWAPStatus.ts.desc())
    
    result = await db.execute(query)
    rows = result.scalars().all()
    
    if not rows:
        raise HTTPException(status_code=404, detail=f"TWAP ID {twap_id} not found")
    
    # Build response
    twap_rows = []
    for row in rows:
        twap_row = TWAPRow(
            wallet=row.wallet,
            ts=row.ts,
            asset=row.asset,
            side=row.side,
            size_requested=str(row.size_requested) if row.size_requested is not None else None,
            size_executed=str(row.size_executed) if row.size_executed is not None else None,
            notional_executed=str(row.notional_executed) if row.notional_executed is not None else None,
            status=row.status,
            duration_minutes=row.duration_minutes,
            raw=row.raw_payload or {}
        )
        twap_rows.append(twap_row)
    
    return TWAPDetailResponse(
        twap_id=twap_id,
        rows=twap_rows
    )


@app.get("/healthz", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint.
    
    Returns service status, database connectivity, and last ingested S3 object.
    """
    db_status = "unknown"
    last_object = None
    last_ingested_at = None
    
    try:
        # Check database connectivity
        await db.execute(text("SELECT 1"))
        db_status = "connected"
        
        # Get last ingested object
        query = select(ETLIngestLog).where(
            ETLIngestLog.error_text.is_(None)
        ).order_by(ETLIngestLog.ingested_at.desc()).limit(1)
        
        result = await db.execute(query)
        last_log = result.scalar_one_or_none()
        
        if last_log:
            last_object = last_log.s3_object_key
            last_ingested_at = last_log.ingested_at
        
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        database=db_status,
        last_ingested_object=last_object,
        last_ingested_at=last_ingested_at
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Hyperliquid TWAP Data Service",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/healthz",
        "metrics": "/metrics"
    }


@app.get("/metrics")
async def get_metrics():
    """
    Prometheus-style metrics endpoint.
    
    Returns metrics in Prometheus text format including:
    - API request counts and durations by endpoint
    - ETL run counts and failures
    - Last ETL run timestamp
    """
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(
        content=metrics.get_prometheus_metrics(),
        media_type="text/plain"
    )
