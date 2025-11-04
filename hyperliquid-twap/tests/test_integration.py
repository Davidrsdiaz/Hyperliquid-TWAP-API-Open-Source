"""End-to-end integration tests for the complete pipeline."""

import os
from datetime import datetime, timezone
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.api.main import app
from src.api.database import get_db
from src.etl.loader import TWAPLoader
from src.etl.parser import TWAPParser

# Test database URL (async)
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://hyperliquid:password@localhost:5432/hyperliquid_test"
)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_etl_to_api_pipeline(tmp_path):
    """
    End-to-end test: Load parquet → Run ETL → Query API → Verify data.
    
    This test validates the complete pipeline:
    1. Create sample parquet data
    2. Run ETL loader to insert data
    3. Query API endpoint
    4. Verify TWAPs are correctly grouped by twap_id
    """
    # Setup async database
    async_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async_session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Clean up any existing test data
        await session.execute(text("DELETE FROM twap_status WHERE wallet = 'test_integration_wallet'"))
        await session.execute(text("DELETE FROM etl_s3_ingest_log WHERE s3_object_key LIKE 'test_integration%'"))
        await session.commit()
    
    # Step 1: Create sample parquet file (use existing sample data generator)
    sample_parquet_path = Path(__file__).parent / "data" / "sample_twap.parquet"
    
    if not sample_parquet_path.exists():
        pytest.skip("Sample parquet file not found. Run tests/create_sample_data.py first.")
    
    # Step 2: Parse the parquet file
    s3_object_key = "test_integration/sample.parquet"
    records = TWAPParser.parse_parquet_file(str(sample_parquet_path), s3_object_key)
    
    # Modify records to use a unique test wallet
    test_wallet = "test_integration_wallet"
    for record in records:
        record["wallet"] = test_wallet
    
    assert len(records) > 0, "Should have parsed records from sample parquet"
    
    # Step 3: Load records using ETL loader
    loader = TWAPLoader()
    try:
        rows_inserted = loader.load_records(records, s3_object_key)
        assert rows_inserted > 0, f"Should have inserted records, got {rows_inserted}"
        
        # Mark as processed
        loader.mark_object_processed(
            s3_object_key,
            datetime.now(timezone.utc),
            rows_inserted
        )
    finally:
        loader.close()
    
    # Step 4: Query API to verify data
    async def override_get_db():
        async with async_session() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Query for our test wallet
            response = await client.get(
                "/api/v1/twaps",
                params={
                    "wallet": test_wallet,
                    "start": "2020-01-01T00:00:00Z",
                    "end": "2030-12-31T23:59:59Z",
                }
            )
            
            assert response.status_code == 200, f"API returned {response.status_code}: {response.text}"
            
            data = response.json()
            
            # Step 5: Verify response structure
            assert data["wallet"] == test_wallet
            assert "twaps" in data
            assert len(data["twaps"]) > 0, "Should have at least one TWAP"
            
            # Verify TWAPs are grouped by twap_id
            twap_ids = [twap["twap_id"] for twap in data["twaps"]]
            assert len(twap_ids) == len(set(twap_ids)), "TWAP IDs should be unique (grouped)"
            
            # Verify each TWAP has expected fields
            for twap in data["twaps"]:
                assert "twap_id" in twap
                assert "asset" in twap
                assert "side" in twap
                assert "status" in twap
                assert "latest_ts" in twap
                assert "executed" in twap
                assert "size" in twap["executed"] or twap["executed"]["size"] is None
                assert "notional" in twap["executed"] or twap["executed"]["notional"] is None
            
            # Step 6: Test pagination
            response_page1 = await client.get(
                "/api/v1/twaps",
                params={
                    "wallet": test_wallet,
                    "start": "2020-01-01T00:00:00Z",
                    "end": "2030-12-31T23:59:59Z",
                    "limit": 1,
                    "offset": 0,
                }
            )
            
            assert response_page1.status_code == 200
            page1_data = response_page1.json()
            assert len(page1_data["twaps"]) <= 1, "Should respect limit parameter"
            
            if len(data["twaps"]) > 1:
                response_page2 = await client.get(
                    "/api/v1/twaps",
                    params={
                        "wallet": test_wallet,
                        "start": "2020-01-01T00:00:00Z",
                        "end": "2030-12-31T23:59:59Z",
                        "limit": 1,
                        "offset": 1,
                    }
                )
                
                assert response_page2.status_code == 200
                page2_data = response_page2.json()
                
                # Ensure pages have different TWAPs
                if len(page1_data["twaps"]) > 0 and len(page2_data["twaps"]) > 0:
                    assert page1_data["twaps"][0]["twap_id"] != page2_data["twaps"][0]["twap_id"]
    
    finally:
        app.dependency_overrides.clear()
        await async_engine.dispose()
    
    # Cleanup
    async with async_session() as session:
        await session.execute(text("DELETE FROM twap_status WHERE wallet = 'test_integration_wallet'"))
        await session.execute(text("DELETE FROM etl_s3_ingest_log WHERE s3_object_key LIKE 'test_integration%'"))
        await session.commit()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_etl_idempotency_integration(tmp_path):
    """
    Test that running ETL twice on the same data doesn't create duplicates.
    """
    sample_parquet_path = Path(__file__).parent / "data" / "sample_twap.parquet"
    
    if not sample_parquet_path.exists():
        pytest.skip("Sample parquet file not found")
    
    s3_object_key = "test_idempotency/sample.parquet"
    
    # Parse records
    records = TWAPParser.parse_parquet_file(str(sample_parquet_path), s3_object_key)
    
    # Modify to use unique wallet
    test_wallet = "test_idempotency_wallet"
    for record in records:
        record["wallet"] = test_wallet
    
    loader = TWAPLoader()
    
    try:
        # First load
        rows_first = loader.load_records(records, s3_object_key)
        assert rows_first > 0
        
        # Second load (should insert 0 due to conflict)
        rows_second = loader.load_records(records, s3_object_key)
        assert rows_second == 0, f"Second load should insert 0 rows, got {rows_second}"
        
        # Verify only one copy exists in database
        async_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
        async with async_engine.connect() as conn:
            result = await conn.execute(
                text("SELECT COUNT(*) FROM twap_status WHERE wallet = :wallet"),
                {"wallet": test_wallet}
            )
            count = result.scalar()
            assert count == rows_first, f"Should have exactly {rows_first} rows, found {count}"
        
        await async_engine.dispose()
        
    finally:
        loader.close()
        
        # Cleanup
        loader2 = TWAPLoader()
        session = loader2.Session()
        try:
            session.execute(
                text("DELETE FROM twap_status WHERE wallet = :wallet"),
                {"wallet": test_wallet}
            )
            session.commit()
        finally:
            session.close()
            loader2.close()
