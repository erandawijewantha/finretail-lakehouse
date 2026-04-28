from __future__ import annotations

from pathlib import Path

import boto3
from botocore.client import Config

from src.config.settings import settings
from src.utils.logger import get_logger 

logger = get_logger(__name__)

def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=f"http{'s' if settings.minio_secure else ''}://{settings.minio_endpoint}",
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
        config=Config(signature_version='s3v4'),
        region_name="us-east-1",
    )

def ensure_bucket_exists() -> None:
    client = get_s3_client()
    buckets = client.list_buckets()
    bucket_names = [bucket["Name"] for bucket in buckets.get("Buckets", [])]
    
    if settings.minio_bucket not in bucket_names:
        client.create_bucket(Bucket=settings.minio_bucket)
        logger.info("Created MinIO bucket: %s", settings.minio_bucket)
    else:
        logger.info("MinIO bucket already exists: %s", settings.minio_bucket)
        
def upload_file(local_path: Path, object_key: str) -> None:
    client = get_s3_client()
    
    client.upload_file(
        Filename=str(local_path),
        Bucket=settings.minio_bucket,
        Key=object_key,
    )
    
    logger.info("Uploaded %s to s3://%s/%s", local_path, settings.minio_bucket, object_key)
    
def list_objects(prefix: str = "") -> list[str]:
    client = get_s3_client()
    
    response = client.list_objects_v2(
        Bucket = settings.minio_bucket,
        Prefix=prefix,
    )
    
    return [item["Key"] for item in response.get("Contents", [])]