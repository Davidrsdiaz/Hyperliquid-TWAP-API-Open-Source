"""Configuration for ETL process."""

import os

from dotenv import load_dotenv

load_dotenv()


class ETLConfig:
    """ETL configuration from environment variables."""

    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "artemis-hyperliquid-data")
    AWS_S3_PREFIX = os.getenv("AWS_S3_PREFIX", "raw/twap_statuses/")
    AWS_REQUEST_PAYER = os.getenv("AWS_REQUEST_PAYER", "requester")
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Batch size for database inserts
    BATCH_SIZE = int(os.getenv("ETL_BATCH_SIZE", "1000"))
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is required")
        
        return True
