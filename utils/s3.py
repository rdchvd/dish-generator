import io
from typing import BinaryIO

import boto3

import settings


class S3Storage:
    """This is class for connect to S3 and uploading/removing files."""

    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
        )

    def upload(self, key: str, file_obj: BinaryIO) -> None:
        self.s3_client.upload_fileobj(
            io.BytesIO(file_obj), settings.AWS_BUCKET_USER_MEDIA_NAME, key
        )

    def delete_object(self, key: str) -> None:
        self.s3_client.delete_object(
            Bucket=settings.AWS_BUCKET_USER_MEDIA_NAME, Key=key
        )

    def get_url(self, key: str) -> str:
        return (
            f"https://s3-{settings.AWS_BUCKET_USER_MEDIA_REGION}"
            f".amazonaws.com/{settings.AWS_BUCKET_USER_MEDIA_NAME}/{key}"
        )
