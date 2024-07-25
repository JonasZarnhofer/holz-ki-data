from fastapi import UploadFile
import crud.image
from db.session import session
from api.model.image import Image, ImageSchema
from db.model import ImageDB, MetadataDB
from db.minio import client, PRODUCTIVE_BUCKET, TEST_BUCKET, TRAIN_BUCKET
import io
from api.model.metadata import Metadata
from categories import CATEGORIES
from minio.helpers import ObjectWriteResult
import hashlib


def _add_image(
    image: UploadFile,
    metadata: Metadata,
    object_prefix: str,
    bucket: str = PRODUCTIVE_BUCKET,
) -> ObjectWriteResult:
    image_hash = hashlib.sha256(image.file.read()).hexdigest()
    print(image_hash)

    with session.begin():
        metadatadb = MetadataDB(metadata.capture_datetime)
        session.add(metadatadb)
        session.flush()
        print(metadatadb.id)
        imagedb = ImageDB(image_hash=image_hash, metadata_id=metadatadb.id)
        session.add(imagedb)

        try:
            result = client.put_object(
                bucket,
                object_prefix + "/" + image_hash,
                image.file,
                length=-1,
                part_size=10 * 1024 * 1024,
                content_type=image.content_type,
            )
        except Exception as e:
            session.rollback()
            raise e

        session.commit()

    return result


def add_train_image(
    image: UploadFile, category: str, metadata: Metadata
) -> ObjectWriteResult:
    if category not in CATEGORIES:
        raise ValueError(f"Category must be in {CATEGORIES}.")

    return _add_image(image, metadata, category, TRAIN_BUCKET)


def add_test_image(
    image: UploadFile, category: str, metadata: Metadata
) -> ObjectWriteResult:
    if category not in CATEGORIES:
        raise ValueError(f"Category must be in {CATEGORIES}.")

    return _add_image(image, metadata, category, TEST_BUCKET)
