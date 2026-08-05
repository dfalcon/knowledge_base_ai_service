"""MinIO / S3 access. Documents are uploaded by Laravel; this service only reads."""

import os

import boto3
from botocore.config import Config

BUCKET = os.getenv("MINIO_BUCKET", "intellibase")

s3_client = boto3.client(
    "s3",
    endpoint_url=os.getenv("AWS_ENDPOINT", "http://localhost:9000"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "minioadmin"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    # MinIO serves buckets as a path, not as a vhost subdomain like real S3.
    config=Config(s3={"addressing_style": "path"}),
)


async def download_file(key: str, destination: str, bucket: str = BUCKET) -> None:
    s3_client.download_file(bucket, key, destination)
