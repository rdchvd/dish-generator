from utils.s3 import S3Storage


def set_photo_uri(cls, value):
    return S3Storage.get_url(value)


def validate_float(cls, value):
    return float(value) if value else None
