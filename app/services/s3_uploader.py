import os
import uuid

import boto3

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("s3_uploader")


def upload_file_to_s3(file_path: str, object_name: str | None = None) -> str | None:
    """
    Uploads local audio file to AWS S3 bucket and returns public URL.
    Falls back cleanly to mock URL if S3 bucket is unconfigured.
    """
    if not os.path.exists(file_path):
        logger.error(f"Target upload file not found: {file_path}")
        return None

    if not settings.AWS_S3_BUCKET_NAME:
        mock_path = object_name or os.path.basename(file_path)
        logger.info(f"S3 unconfigured. Using mock URL for {file_path} -> {mock_path}")
        return f"https://mock-storage.musicanalyser.io/{mock_path}"

    if not object_name:
        ext = os.path.splitext(file_path)[1]
        object_name = f"songs/uploads/{uuid.uuid4()}{ext}"

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )

    try:
        s3_client.upload_file(file_path, settings.AWS_S3_BUCKET_NAME, object_name)
        url = f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{object_name}"
        logger.info(f"S3 upload successful: {url}")
        return url
    except Exception as e:
        logger.error(f"S3 error during upload: {e}")
        return None
