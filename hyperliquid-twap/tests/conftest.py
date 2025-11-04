"""Pytest configuration and fixtures."""

import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Set test database URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://hyperliquid:password@localhost:5432/hyperliquid_test"
)


@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine."""
    # Convert async URL to sync for testing
    db_url = TEST_DATABASE_URL
    if "asyncpg" in db_url:
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    
    engine = create_engine(db_url)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_db_engine):
    """Provide a clean database session for each test."""
    Session = sessionmaker(bind=test_db_engine)
    session = Session()
    
    # Read and execute schema
    schema_path = Path(__file__).parent.parent / "src" / "db" / "schema.sql"
    with open(schema_path) as f:
        schema_sql = f.read()
    
    # Create tables
    for statement in schema_sql.split(";"):
        if statement.strip():
            session.execute(text(statement))
    session.commit()
    
    yield session
    
    # Cleanup - drop tables
    session.execute(text("DROP TABLE IF EXISTS twap_status CASCADE"))
    session.execute(text("DROP TABLE IF EXISTS etl_s3_ingest_log CASCADE"))
    session.commit()
    session.close()


@pytest.fixture
def sample_parquet_path():
    """Path to sample parquet file."""
    return Path(__file__).parent / "data" / "sample_twap.parquet"
