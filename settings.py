import os

from dotenv import load_dotenv

load_dotenv()


DEBUG = os.getenv("DEBUG", "False") == "True"

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT"))
POSTGRES_DB = os.getenv("POSTGRES_DB")

POSTGRES_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# AWS
S3_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID", "")
S3_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY", "")
S3_USER_MEDIA_NAME = os.getenv("S3_USER_MEDIA_NAME", "")
S3_USER_MEDIA_REGION = os.getenv("S3_USER_MEDIA_REGION", "")
