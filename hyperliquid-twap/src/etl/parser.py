"""Parquet file parser for TWAP data."""

import io
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

import pandas as pd
import pyarrow.parquet as pq

logger = logging.getLogger(__name__)


class TWAPParser:
    """Parser for Hyperliquid TWAP parquet files."""

    # Column mapping from parquet to database
    COLUMN_MAPPING = {
        "twap_id": "twap_id",
        "state_user": "wallet",
        "state_timestamp": "ts",
        "state_coin": "asset",
        "state_side": "side",
        "state_sz": "size_requested",
        "state_executedSz": "size_executed",
        "state_executedNtl": "notional_executed",
        "status": "status",
        "state_minutes": "duration_minutes",
    }

    @staticmethod
    def parse_parquet(content: bytes, s3_object_key: str) -> List[Dict[str, Any]]:
        """
        Parse parquet content into database-ready records.
        
        Args:
            content: Parquet file content as bytes
            s3_object_key: S3 key for tracking
            
        Returns:
            List of record dictionaries
        """
        try:
            # Read parquet from bytes
            buffer = io.BytesIO(content)
            table = pq.read_table(buffer)
            df = table.to_pandas()
            
            logger.info(f"Parsed {len(df)} rows from parquet")
            
            # Convert to records
            records = []
            for _, row in df.iterrows():
                record = TWAPParser._row_to_record(row, s3_object_key)
                records.append(record)
            
            return records
            
        except Exception as e:
            logger.error(f"Error parsing parquet: {e}")
            raise

    @staticmethod
    def parse_parquet_file(filepath: str, s3_object_key: str = "local") -> List[Dict[str, Any]]:
        """
        Parse parquet file from local filesystem.
        
        Args:
            filepath: Path to parquet file
            s3_object_key: S3 key for tracking (default: 'local')
            
        Returns:
            List of record dictionaries
        """
        try:
            df = pd.read_parquet(filepath)
            logger.info(f"Parsed {len(df)} rows from {filepath}")
            
            records = []
            for _, row in df.iterrows():
                record = TWAPParser._row_to_record(row, s3_object_key)
                records.append(record)
            
            return records
            
        except Exception as e:
            logger.error(f"Error parsing parquet file {filepath}: {e}")
            raise

    @staticmethod
    def _row_to_record(row: pd.Series, s3_object_key: str) -> Dict[str, Any]:
        """
        Convert a pandas row to a database record.
        
        Args:
            row: Pandas series representing a row
            s3_object_key: S3 key for tracking
            
        Returns:
            Dictionary ready for database insertion
        """
        record = {}
        
        # Map columns according to schema
        for parquet_col, db_col in TWAPParser.COLUMN_MAPPING.items():
            if parquet_col in row.index:
                value = row[parquet_col]
                
                # Handle timestamp conversion
                if db_col == "ts":
                    value = TWAPParser._normalize_timestamp(value)
                
                # Handle pandas NA/NaN values
                if pd.isna(value):
                    value = None
                
                record[db_col] = value
            else:
                # Column not present in parquet, set to None
                record[db_col] = None
        
        # Add metadata
        record["s3_object_key"] = s3_object_key
        
        # Store entire row as JSON for forward compatibility
        raw_payload = row.to_dict()
        # Convert timestamps and NaN values for JSON serialization
        for key, value in raw_payload.items():
            if pd.isna(value):
                raw_payload[key] = None
            elif isinstance(value, pd.Timestamp):
                raw_payload[key] = value.isoformat()
        
        record["raw_payload"] = raw_payload
        
        return record

    @staticmethod
    def _normalize_timestamp(ts: Any) -> datetime:
        """
        Normalize timestamp to UTC-aware datetime.
        
        Args:
            ts: Timestamp value (various formats)
            
        Returns:
            UTC-aware datetime object
        """
        if isinstance(ts, pd.Timestamp):
            dt = ts.to_pydatetime()
        elif isinstance(ts, datetime):
            dt = ts
        elif isinstance(ts, str):
            dt = pd.to_datetime(ts).to_pydatetime()
        elif isinstance(ts, (int, float)):
            # Assume Unix timestamp
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        else:
            raise ValueError(f"Unsupported timestamp type: {type(ts)}")
        
        # Ensure UTC timezone
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        
        return dt
