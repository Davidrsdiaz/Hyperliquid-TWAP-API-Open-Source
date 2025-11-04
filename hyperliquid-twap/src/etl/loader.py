"""Database loader for TWAP data."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from sqlalchemy import create_engine, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker

from ..db.models import ETLIngestLog, TWAPStatus
from .config import ETLConfig

logger = logging.getLogger(__name__)


class TWAPLoader:
    """Loader for inserting TWAP data into PostgreSQL."""

    def __init__(self):
        """Initialize database connection."""
        # Convert async URL to sync for SQLAlchemy Core operations
        db_url = ETLConfig.DATABASE_URL
        if "asyncpg" in db_url:
            db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
        
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def load_records(self, records: List[Dict[str, Any]], s3_object_key: str) -> int:
        """
        Load records into the database with ON CONFLICT DO NOTHING.
        
        Args:
            records: List of record dictionaries
            s3_object_key: S3 object key being processed
            
        Returns:
            Number of rows inserted
        """
        if not records:
            logger.warning("No records to load")
            return 0
        
        session = self.Session()
        rows_inserted = 0
        
        try:
            # Insert records in batches
            batch_size = ETLConfig.BATCH_SIZE
            
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                
                # Use INSERT ... ON CONFLICT DO NOTHING
                stmt = insert(TWAPStatus.__table__).values(batch)
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=["twap_id", "wallet", "ts"]
                )
                
                result = session.execute(stmt)
                rows_inserted += result.rowcount
                
                logger.info(
                    f"Inserted batch {i // batch_size + 1}: "
                    f"{result.rowcount} rows (total: {rows_inserted})"
                )
            
            session.commit()
            logger.info(f"Successfully loaded {rows_inserted} records")
            
            return rows_inserted
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error loading records: {e}")
            raise
        finally:
            session.close()

    def mark_object_processed(
        self,
        s3_object_key: str,
        last_modified: datetime,
        rows_ingested: int,
        error_text: str = None
    ):
        """
        Mark an S3 object as processed in the ingest log.
        
        Args:
            s3_object_key: S3 object key
            last_modified: Object's last modified timestamp
            rows_ingested: Number of rows ingested
            error_text: Optional error message if processing failed
        """
        session = self.Session()
        
        try:
            stmt = insert(ETLIngestLog.__table__).values(
                s3_object_key=s3_object_key,
                last_modified=last_modified,
                rows_ingested=rows_ingested,
                error_text=error_text
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=["s3_object_key"],
                set_={
                    "last_modified": last_modified,
                    "rows_ingested": rows_ingested,
                    "error_text": error_text,
                    "ingested_at": datetime.now(timezone.utc)
                }
            )
            
            session.execute(stmt)
            session.commit()
            
            logger.info(f"Marked {s3_object_key} as processed")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error marking object as processed: {e}")
            raise
        finally:
            session.close()

    def get_processed_objects(self) -> set:
        """
        Get set of already processed S3 object keys.
        
        Returns:
            Set of S3 object keys
        """
        session = self.Session()
        
        try:
            result = session.execute(
                text("SELECT s3_object_key FROM etl_s3_ingest_log WHERE error_text IS NULL")
            )
            
            processed = {row[0] for row in result}
            logger.info(f"Found {len(processed)} already processed objects")
            
            return processed
            
        finally:
            session.close()

    def close(self):
        """Close database connection."""
        self.engine.dispose()
