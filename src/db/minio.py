from minio import Minio
import os


MINIO_HOST = os.getenv("MINIO_HOST")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")

client = Minio(MINIO_HOST, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, secure=False)

TRAIN_BUCKET = "train"
TEST_BUCKET = "test"
PRODUCTIVE_BUCKET = "productive"

found = client.bucket_exists(TRAIN_BUCKET)
if not found:
    client.make_bucket(TRAIN_BUCKET)

found = client.bucket_exists(TEST_BUCKET)
if not found:
    client.make_bucket(TEST_BUCKET)

found = client.bucket_exists(PRODUCTIVE_BUCKET)
if not found:
    client.make_bucket(PRODUCTIVE_BUCKET)
