"""Pytest configuration and fixtures."""

import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker

# Set test database URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://hyperliquid:password@localhost:5432/hyperliquid_test"
)


@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine and initialize schema once per session."""
    # Convert async URL to sync for testing
    db_url = TEST_DATABASE_URL
    if "asyncpg" in db_url:
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    
    engine = create_engine(db_url, echo=False)
    
    # Create tables once at session start
    schema_path = Path(__file__).parent.parent / "src" / "db" / "schema.sql"
    with open(schema_path) as f:
        schema_sql = f.read()
    
    with engine.begin() as conn:
        # Drop tables if they exist (clean slate)
        conn.execute(text("DROP TABLE IF EXISTS twap_status CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS etl_s3_ingest_log CASCADE"))
        
        # Create tables
        for statement in schema_sql.split(";"):
            if statement.strip():
                conn.execute(text(statement))
    
    yield engine
    
    # Cleanup at session end
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS twap_status CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS etl_s3_ingest_log CASCADE"))
    
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_db_engine):
    """
    Provide a clean database session for each test using transaction rollback.
    
    This fixture creates a nested transaction that is rolled back after each test,
    providing isolation without the overhead of dropping/recreating tables.
    """
    # Create a connection and begin a transaction
    connection = test_db_engine.connect()
    transaction = connection.begin()
    
    # Create a session bound to the connection
    Session = sessionmaker(bind=connection)
    session = Session()
    
    # Begin a nested transaction (savepoint)
    nested = connection.begin_nested()
    
    # If the application code calls session.commit(), it will only commit
    # the nested transaction (savepoint), not the outer transaction
    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.expire_all()
            session.begin_nested()
    
    yield session
    
    # Rollback the outer transaction (undoes all changes)
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def sample_parquet_path():
    """Path to sample parquet file."""
    return Path(__file__).parent / "data" / "sample_twap.parquet"
