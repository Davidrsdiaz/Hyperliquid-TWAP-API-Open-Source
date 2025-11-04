"""Database initialization script."""

import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_sync_db_url() -> str:
    """Convert async database URL to sync URL for psycopg2."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    # Replace asyncpg with psycopg for synchronous connection
    if "asyncpg" in db_url:
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    
    return db_url


def init_db():
    """Initialize the database schema using the SQL file."""
    db_url = get_sync_db_url()
    
    # Parse connection URL using urllib for proper handling of special characters
    try:
        parsed = urlparse(db_url)
        
        if not parsed.scheme.startswith("postgresql"):
            raise ValueError(f"Invalid database URL scheme: {parsed.scheme}")
        
        host = parsed.hostname or "localhost"
        port = parsed.port or 5432
        dbname = parsed.path.lstrip("/") or "postgres"
        user = parsed.username or "postgres"
        password = parsed.password or ""
        
    except Exception as e:
        print(f"Error parsing DATABASE_URL: {e}")
        print(f"Expected format: postgresql://user:password@host:port/database")
        sys.exit(1)
    
    print(f"Connecting to database at {host}:{port}/{dbname}")
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=dbname,
            user=user,
            password=password
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Read schema file
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path, "r") as f:
            schema_sql = f.read()
        
        # Execute schema
        print("Creating database schema...")
        cursor.execute(schema_sql)
        
        print("Database schema initialized successfully!")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    init_db()
