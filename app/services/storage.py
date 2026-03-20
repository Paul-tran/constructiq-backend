import os
import uuid
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from fastapi import HTTPException

APP_ENV = os.getenv("APP_ENV", "development")

# --- Client factory ---

def _get_client():
    if APP_ENV == "production":
        return boto3.client(
            "s3",
            endpoint_url=os.getenv("R2_ENDPOINT"),
            aws_access_key_id=os.getenv("R2_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("R2_SECRET_KEY"),
            config=Config(signature_version="s3v4"),
        ), os.getenv("R2_BUCKET", "constructiq-files")
    else:
        secure = os.getenv("MINIO_SECURE", "False").lower() == "true"
        endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
        return boto3.client(
            "s3",
            endpoint_url=f"{'https' if secure else 'http'}://{endpoint}",
            aws_access_key_id=os.getenv("MINIO_ACCESS_KEY", "constructiq"),
            aws_secret_access_key=os.getenv("MINIO_SECRET_KEY", "constructiq123"),
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",  # Required by boto3, ignored by MinIO
        ), os.getenv("MINIO_BUCKET", "constructiq-files")


def _ensure_bucket(client, bucket: str):
    """Create the bucket if it doesn't exist (dev only)."""
    try:
        client.head_bucket(Bucket=bucket)
    except ClientError:
        client.create_bucket(Bucket=bucket)


# --- Public interface ---

def make_file_key(module: str, project_id: int, filename: str) -> str:
    """Generate a unique storage key: documents/42/uuid4/drawing.pdf"""
    ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
    unique = uuid.uuid4().hex
    return f"{module}/{project_id}/{unique}/{filename}" if not ext else f"{module}/{project_id}/{unique}/{filename}"


def upload_file(file_bytes: bytes, file_key: str, content_type: str) -> str:
    """Upload bytes to storage. Returns the file_key."""
    client, bucket = _get_client()

    if APP_ENV != "production":
        _ensure_bucket(client, bucket)

    try:
        client.put_object(
            Bucket=bucket,
            Key=file_key,
            Body=file_bytes,
            ContentType=content_type,
        )
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

    return file_key


def get_presigned_url(file_key: str, expires: int = 3600) -> str:
    """Return a presigned URL valid for `expires` seconds."""
    client, bucket = _get_client()
    try:
        url = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": file_key},
            ExpiresIn=expires,
        )
        return url
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Could not generate URL: {e}")


def delete_file(file_key: str) -> None:
    """Delete a file from storage."""
    client, bucket = _get_client()
    try:
        client.delete_object(Bucket=bucket, Key=file_key)
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {e}")
