"""Tests for ETL module."""

from pathlib import Path

import pytest
from sqlalchemy import text

from src.etl.loader import TWAPLoader
from src.etl.parser import TWAPParser


def test_parse_sample_parquet(sample_parquet_path):
    """Test parsing sample parquet file."""
    if not sample_parquet_path.exists():
        pytest.skip("Sample parquet file not found")
    
    records = TWAPParser.parse_parquet_file(str(sample_parquet_path), "test_key")
    
    assert len(records) > 0
    
    # Check first record has expected fields
    record = records[0]
    assert "twap_id" in record
    assert "wallet" in record
    assert "ts" in record
    assert "asset" in record
    assert "s3_object_key" in record
    assert record["s3_object_key"] == "test_key"


def test_loader_idempotency(test_db, sample_parquet_path):
    """Test that loading the same data twice doesn't duplicate rows."""
    if not sample_parquet_path.exists():
        pytest.skip("Sample parquet file not found")
    
    # Parse sample data
    records = TWAPParser.parse_parquet_file(str(sample_parquet_path), "test_key")
    
    # Create loader (use sync engine from test fixture)
    loader = TWAPLoader()
    
    # First load
    rows_first = loader.load_records(records, "test_key")
    
    # Second load (should insert 0 rows due to conflict)
    rows_second = loader.load_records(records, "test_key")
    
    assert rows_first > 0
    assert rows_second == 0
    
    # Verify total rows in database
    result = test_db.execute(text("SELECT COUNT(*) FROM twap_status"))
    count = result.scalar()
    assert count == rows_first
    
    loader.close()


def test_ingest_log_tracking(test_db):
    """Test that processed objects are tracked in ingest log."""
    from datetime import datetime, timezone
    
    loader = TWAPLoader()
    
    # Mark object as processed
    loader.mark_object_processed(
        "s3://test/key.parquet",
        datetime.now(timezone.utc),
        100
    )
    
    # Check it's in the processed set
    processed = loader.get_processed_objects()
    assert "s3://test/key.parquet" in processed
    
    loader.close()
