"""Async tests for API endpoints with database operations."""

from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.api.main import app
from src.api.database import get_db
from src.db.models import TWAPStatus

# Test database URL (async)
TEST_DATABASE_URL = "postgresql+asyncpg://hyperliquid:password@localhost:5432/hyperliquid_test"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_engine():
    """Create async database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    yield engine
    await engine.dispose()


@pytest.fixture
async def async_db(async_engine):
    """Provide async database session for tests."""
    async_session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Begin transaction
        async with session.begin():
            yield session
            # Transaction will be rolled back after test


@pytest.fixture
async def async_client(async_db):
    """Create async test client with database override."""
    async def override_get_db():
        yield async_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
async def sample_data(async_db):
    """Insert sample TWAP data for testing."""
    sample_records = [
        {
            "twap_id": "test123",
            "wallet": "0xtest_wallet",
            "ts": datetime(2025, 11, 3, 12, 0, 0, tzinfo=timezone.utc),
            "asset": "SOL",
            "side": "B",
            "size_requested": 100.0,
            "size_executed": 50.0,
            "notional_executed": 4525.0,
            "status": "executing",
            "duration_minutes": 30,
            "s3_object_key": "test/key1.parquet",
            "raw_payload": {"test": "data"},
        },
        {
            "twap_id": "test123",
            "wallet": "0xtest_wallet",
            "ts": datetime(2025, 11, 3, 12, 15, 0, tzinfo=timezone.utc),
            "asset": "SOL",
            "side": "B",
            "size_requested": 100.0,
            "size_executed": 100.0,
            "notional_executed": 9050.0,
            "status": "completed",
            "duration_minutes": 30,
            "s3_object_key": "test/key1.parquet",
            "raw_payload": {"test": "data2"},
        },
        {
            "twap_id": "test456",
            "wallet": "0xtest_wallet",
            "ts": datetime(2025, 11, 3, 14, 0, 0, tzinfo=timezone.utc),
            "asset": "ETH",
            "side": "A",
            "size_requested": 5.0,
            "size_executed": 2.5,
            "notional_executed": 8500.0,
            "status": "executing",
            "duration_minutes": 60,
            "s3_object_key": "test/key2.parquet",
            "raw_payload": {"test": "data3"},
        },
    ]
    
    # Insert using SQLAlchemy Core
    stmt = insert(TWAPStatus.__table__).values(sample_records)
    await async_db.execute(stmt)
    await async_db.commit()
    
    return sample_records


@pytest.mark.asyncio
async def test_get_twaps_with_data(async_client, sample_data):
    """Test GET /api/v1/twaps returns correctly grouped data."""
    response = await async_client.get(
        "/api/v1/twaps",
        params={
            "wallet": "0xtest_wallet",
            "start": "2025-11-03T00:00:00Z",
            "end": "2025-11-04T00:00:00Z",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["wallet"] == "0xtest_wallet"
    assert len(data["twaps"]) == 2  # Two distinct twap_ids
    
    # Check that data is grouped by twap_id
    twap_ids = {twap["twap_id"] for twap in data["twaps"]}
    assert twap_ids == {"test123", "test456"}
    
    # Check latest_per_twap logic (should return latest timestamp per twap)
    test123 = next(t for t in data["twaps"] if t["twap_id"] == "test123")
    assert test123["status"] == "completed"  # Latest status
    assert test123["executed"]["size"] == "100.0"


@pytest.mark.asyncio
async def test_get_twaps_with_asset_filter(async_client, sample_data):
    """Test asset filtering works correctly."""
    response = await async_client.get(
        "/api/v1/twaps",
        params={
            "wallet": "0xtest_wallet",
            "start": "2025-11-03T00:00:00Z",
            "end": "2025-11-04T00:00:00Z",
            "asset": "SOL",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["twaps"]) == 1
    assert data["twaps"][0]["asset"] == "SOL"
    assert data["twaps"][0]["twap_id"] == "test123"


@pytest.mark.asyncio
async def test_get_twaps_empty_result(async_client, sample_data):
    """Test query with no matching data returns empty list."""
    response = await async_client.get(
        "/api/v1/twaps",
        params={
            "wallet": "0xnonexistent",
            "start": "2025-11-03T00:00:00Z",
            "end": "2025-11-04T00:00:00Z",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["wallet"] == "0xnonexistent"
    assert len(data["twaps"]) == 0


@pytest.mark.asyncio
async def test_get_twap_by_id(async_client, sample_data):
    """Test GET /api/v1/twaps/{twap_id} returns all rows."""
    response = await async_client.get("/api/v1/twaps/test123")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["twap_id"] == "test123"
    assert len(data["rows"]) == 2  # Two status updates for this TWAP
    
    # Check rows are ordered by timestamp descending
    timestamps = [row["ts"] for row in data["rows"]]
    assert timestamps == sorted(timestamps, reverse=True)


@pytest.mark.asyncio
async def test_get_twap_by_id_not_found(async_client, sample_data):
    """Test 404 for non-existent TWAP ID."""
    response = await async_client.get("/api/v1/twaps/nonexistent")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_health_check_with_data(async_client, sample_data):
    """Test health check returns database status."""
    response = await async_client.get("/healthz")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] in ["healthy", "degraded"]
    assert "database" in data
    assert "last_ingested_object" in data
