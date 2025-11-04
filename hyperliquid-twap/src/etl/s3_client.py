"""S3 client with requester-pays support."""

import logging
from datetime import datetime
from typing import List, Optional

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from .config import ETLConfig

logger = logging.getLogger(__name__)


class S3Client:
    """S3 client wrapper that always uses RequestPayer for requester-pays buckets."""

    def __init__(self):
        """Initialize S3 client with retry configuration."""
        # Configure retries for transient failures
        config = Config(
            retries={
                'max_attempts': 3,
                'mode': 'adaptive'  # Use adaptive retry mode for better handling
            },
            connect_timeout=5,
            read_timeout=60
        )
        
        self.s3 = boto3.client("s3", region_name=ETLConfig.AWS_REGION, config=config)
        self.bucket = ETLConfig.AWS_S3_BUCKET
        self.prefix = ETLConfig.AWS_S3_PREFIX
        self.request_payer = ETLConfig.AWS_REQUEST_PAYER

    def list_objects(
        self, since: Optional[datetime] = None
    ) -> List[dict]:
        """
        List all objects under the configured prefix.
        
        Args:
            since: Optional datetime to filter objects by LastModified
            
        Returns:
            List of object metadata dictionaries
        """
        objects = []
        continuation_token = None
        
        logger.info(f"Listing objects in s3://{self.bucket}/{self.prefix}")
        
        try:
            while True:
                kwargs = {
                    "Bucket": self.bucket,
                    "Prefix": self.prefix,
                    "RequestPayer": self.request_payer,
                }
                
                if continuation_token:
                    kwargs["ContinuationToken"] = continuation_token
                
                response = self.s3.list_objects_v2(**kwargs)
                
                if "Contents" in response:
                    for obj in response["Contents"]:
                        # Filter by last modified if specified
                        if since and obj["LastModified"] < since:
                            continue
                        
                        objects.append({
                            "key": obj["Key"],
                            "last_modified": obj["LastModified"],
                            "size": obj["Size"],
                        })
                
                # Check if there are more objects
                if not response.get("IsTruncated"):
                    break
                
                continuation_token = response.get("NextContinuationToken")
            
            logger.info(f"Found {len(objects)} objects")
            return objects
            
        except ClientError as e:
            logger.error(f"Error listing S3 objects: {e}")
            raise

    def download_object(self, key: str) -> bytes:
        """
        Download an object from S3.
        
        Args:
            key: S3 object key
            
        Returns:
            Object content as bytes
        """
        logger.info(f"Downloading s3://{self.bucket}/{key}")
        
        try:
            response = self.s3.get_object(
                Bucket=self.bucket,
                Key=key,
                RequestPayer=self.request_payer
            )
            
            content = response["Body"].read()
            logger.info(f"Downloaded {len(content)} bytes")
            return content
            
        except ClientError as e:
            logger.error(f"Error downloading S3 object {key}: {e}")
            raise

    def get_object_metadata(self, key: str) -> dict:
        """
        Get metadata for a single S3 object.
        
        Args:
            key: S3 object key
            
        Returns:
            Object metadata dictionary
        """
        try:
            response = self.s3.head_object(
                Bucket=self.bucket,
                Key=key,
                RequestPayer=self.request_payer
            )
            
            return {
                "key": key,
                "last_modified": response["LastModified"],
                "size": response["ContentLength"],
            }
            
        except ClientError as e:
            logger.error(f"Error getting object metadata for {key}: {e}")
            raise
