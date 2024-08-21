from minio import Minio
import os


MINIO_HOST = os.getenv("MINIO_HOST")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")

client = Minio(MINIO_HOST, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, secure=False)

PRODUCTIVE_BUCKET = "ai-data"

found = client.bucket_exists(PRODUCTIVE_BUCKET)
if not found:
    client.make_bucket(PRODUCTIVE_BUCKET)
