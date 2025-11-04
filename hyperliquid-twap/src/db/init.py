"""Database initialization script."""

import os
import sys
from pathlib import Path

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
    
    # Parse connection URL manually for psycopg2
    # Format: postgresql://user:pass@host:port/dbname
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "")
    
    # Split into components
    if "@" in db_url:
        auth, location = db_url.split("@", 1)
        user, password = auth.split(":", 1) if ":" in auth else (auth, "")
        
        if "/" in location:
            hostport, dbname = location.split("/", 1)
            host, port = hostport.split(":", 1) if ":" in hostport else (hostport, "5432")
        else:
            host, port, dbname = location, "5432", "postgres"
    else:
        raise ValueError(f"Invalid DATABASE_URL format: {db_url}")
    
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
