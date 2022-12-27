import io
from typing import BinaryIO, Optional

import boto3

from settings import (
    S3_ACCESS_KEY_ID,
    S3_SECRET_ACCESS_KEY,
    S3_USER_MEDIA_NAME,
    S3_USER_MEDIA_REGION,
)


class S3Storage:
    """This is class for connect to S3 and uploading/removing files."""

    region = S3_USER_MEDIA_REGION
    bucket = S3_USER_MEDIA_NAME
    secret_access_key = S3_SECRET_ACCESS_KEY
    access_key_id = S3_ACCESS_KEY_ID

    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
        )

    def upload_base64(self, key: str, file_obj: BinaryIO) -> None:
        self.s3_client.upload_fileobj(io.BytesIO(file_obj), self.bucket, key)

    def upload_file(self, key: str, file_obj) -> None:
        self.s3_client.upload_fileobj(file_obj, self.bucket, key)

    def delete_object(self, key: str) -> None:
        self.s3_client.delete_object(Bucket=self.bucket, Key=key)

    @classmethod
    def get_url(cls, key: str) -> Optional[str]:
        if not key:
            return None
        return f"https://s3-{cls.region}.amazonaws.com/{cls.bucket}/{key}"
