"""ETL CLI entrypoint for ingesting TWAP data."""

import argparse
import logging
import os
import sys
from datetime import datetime
from typing import Optional

from dateutil import parser as date_parser

from ..common.logging import setup_structured_logging
from .config import ETLConfig
from .loader import TWAPLoader
from .parser import TWAPParser
from .s3_client import S3Client

# Configure structured logging
use_json_logs = os.getenv("LOG_FORMAT", "json").lower() == "json"
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_structured_logging(level=log_level, use_json=use_json_logs)

logger = logging.getLogger(__name__)


def process_s3_object(
    s3_client: S3Client,
    loader: TWAPLoader,
    object_key: str,
    last_modified: datetime
) -> bool:
    """
    Process a single S3 object.
    
    Args:
        s3_client: S3 client instance
        loader: Database loader instance
        object_key: S3 object key
        last_modified: Object's last modified timestamp
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Processing object: {object_key}")
        
        # Download object
        try:
            content = s3_client.download_object(object_key)
        except Exception as e:
            logger.error(f"Failed to download {object_key}: {e}")
            loader.mark_object_processed(object_key, last_modified, 0, f"Download error: {e}")
            return False
        
        # Parse parquet
        try:
            records = TWAPParser.parse_parquet(content, object_key)
        except Exception as e:
            logger.error(f"Failed to parse {object_key}: {e}")
            loader.mark_object_processed(object_key, last_modified, 0, f"Parse error: {e}")
            return False
        
        if not records:
            logger.warning(f"No records found in {object_key}")
            loader.mark_object_processed(object_key, last_modified, 0)
            return True
        
        # Load into database
        try:
            rows_inserted = loader.load_records(records, object_key)
        except Exception as e:
            logger.error(f"Failed to load records from {object_key}: {e}")
            loader.mark_object_processed(object_key, last_modified, 0, f"Load error: {e}")
            return False
        
        # Mark as processed
        try:
            loader.mark_object_processed(object_key, last_modified, rows_inserted)
        except Exception as e:
            logger.error(f"Failed to mark {object_key} as processed (but data was loaded): {e}")
            # Data was successfully loaded, so we consider this a success
            return True
        
        logger.info(f"Successfully processed {object_key}: {rows_inserted} rows")
        return True
        
    except Exception as e:
        # Catch-all for any unexpected errors
        logger.error(f"Unexpected error processing {object_key}: {e}", exc_info=True)
        try:
            loader.mark_object_processed(object_key, last_modified, 0, f"Unexpected error: {e}")
        except Exception:
            logger.error(f"Failed to mark {object_key} as failed in ingest log")
        return False


def process_local_file(loader: TWAPLoader, filepath: str) -> bool:
    """
    Process a local parquet file.
    
    Args:
        loader: Database loader instance
        filepath: Path to local parquet file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Processing local file: {filepath}")
        
        # Parse parquet
        records = TWAPParser.parse_parquet_file(filepath, f"local:{filepath}")
        
        if not records:
            logger.warning(f"No records found in {filepath}")
            return True
        
        # Load into database
        rows_inserted = loader.load_records(records, f"local:{filepath}")
        
        logger.info(f"Successfully processed {filepath}: {rows_inserted} rows")
        return True
        
    except Exception as e:
        logger.error(f"Failed to process {filepath}: {e}")
        return False


def run_incremental(s3_client: S3Client, loader: TWAPLoader, since: Optional[datetime] = None):
    """
    Run incremental ETL process.
    
    Args:
        s3_client: S3 client instance
        loader: Database loader instance
        since: Optional datetime to filter objects
    """
    logger.info("Starting incremental ETL process")
    
    # Get list of S3 objects
    objects = s3_client.list_objects(since=since)
    
    if not objects:
        logger.info("No new objects to process")
        return
    
    # Get already processed objects
    processed = loader.get_processed_objects()
    
    # Filter out already processed objects
    new_objects = [obj for obj in objects if obj["key"] not in processed]
    
    logger.info(f"Found {len(new_objects)} new objects to process (out of {len(objects)} total)")
    
    # Process each object
    success_count = 0
    fail_count = 0
    
    for obj in new_objects:
        success = process_s3_object(
            s3_client,
            loader,
            obj["key"],
            obj["last_modified"]
        )
        
        if success:
            success_count += 1
        else:
            fail_count += 1
    
    logger.info(
        f"ETL process completed: {success_count} succeeded, {fail_count} failed"
    )


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="ETL process for Hyperliquid TWAP data"
    )
    
    parser.add_argument(
        "--incremental",
        action="store_true",
        default=True,
        help="Process all new S3 objects (default)"
    )
    
    parser.add_argument(
        "--since",
        type=str,
        help="Process objects modified since this ISO8601 date"
    )
    
    parser.add_argument(
        "--object-key",
        type=str,
        help="Process a specific S3 object key"
    )
    
    parser.add_argument(
        "--local-file",
        type=str,
        help="Process a local parquet file (for testing)"
    )
    
    args = parser.parse_args()
    
    try:
        # Validate configuration
        ETLConfig.validate()
        
        # Initialize loader
        loader = TWAPLoader()
        
        # Handle local file processing
        if args.local_file:
            success = process_local_file(loader, args.local_file)
            sys.exit(0 if success else 1)
        
        # Initialize S3 client
        s3_client = S3Client()
        
        # Handle single object processing
        if args.object_key:
            logger.info(f"Processing single object: {args.object_key}")
            metadata = s3_client.get_object_metadata(args.object_key)
            success = process_s3_object(
                s3_client,
                loader,
                args.object_key,
                metadata["last_modified"]
            )
            sys.exit(0 if success else 1)
        
        # Handle incremental processing
        since_date = None
        if args.since:
            since_date = date_parser.isoparse(args.since)
            logger.info(f"Filtering objects since {since_date}")
        
        run_incremental(s3_client, loader, since=since_date)
        
    except Exception as e:
        logger.error(f"ETL process failed: {e}")
        sys.exit(1)
    finally:
        if 'loader' in locals():
            loader.close()


if __name__ == "__main__":
    main()
