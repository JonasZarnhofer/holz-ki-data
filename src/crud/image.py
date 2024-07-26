from api.model.metadata import Metadata, MetadataInternal, MetadataSchema
from api.model.page import Page

from fastapi import UploadFile

import sqlalchemy
import sqlalchemy.exc

from db.session import session
from db.model import ImageDB, MetadataDB, ErrorCategoryDB, DatasetCategoryDB
from db.minio import client, PRODUCTIVE_BUCKET, TEST_BUCKET, TRAIN_BUCKET
from db.utils.enum import DATASET_CATEGORIES_DB, ERROR_CATEGORIES_DB
from db.utils.queries import get_error_id, get_dataset_id

from crud.utils.rollback import crud_exception_handle
from crud.utils.hash import hash_file

from categories import ERROR_CATEGORIES
from minio.helpers import ObjectWriteResult

import zipfile
from tempfile import SpooledTemporaryFile


async def _add_image(
    image: UploadFile,
    metadata: MetadataInternal,
    object_prefix: str,
    bucket: str = PRODUCTIVE_BUCKET,
) -> ObjectWriteResult:
    # Hashing the image to get a unique identifier. Additionally
    # this prevents the same image from being uploaded multiple times.
    image_hash = hash_file(image.file)
    await image.seek(0)

    with session.begin():
        metadatadb = MetadataDB(
            metadata.capture_datetime,
            get_dataset_id(metadata.dataset_type),
            get_error_id(metadata.error_type),
        )
        session.add(metadatadb)
        session.flush()
        imagedb = ImageDB(image_hash=image_hash, metadata_id=metadatadb.id)
        session.add(imagedb)

        await image.seek(0)
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

        try:
            session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            session.rollback()
            raise ValueError("Image already exists.")

    return result


@crud_exception_handle
async def add_train_image(
    image: UploadFile, category: str, metadata: MetadataInternal
) -> ObjectWriteResult:
    if category not in ERROR_CATEGORIES:
        raise ValueError(f"Category must be in {ERROR_CATEGORIES}.")

    return await _add_image(image, metadata, category, TRAIN_BUCKET)


@crud_exception_handle
async def add_test_image(
    image: UploadFile, category: str, metadata: MetadataInternal
) -> ObjectWriteResult:
    if category not in ERROR_CATEGORIES:
        raise ValueError(f"Category must be in {ERROR_CATEGORIES}.")

    return await _add_image(image, metadata, category, TEST_BUCKET)


def train_dataset_zip(page: Page) -> SpooledTemporaryFile:
    imagedb = (
        session.query(ImageDB)
        .join(MetadataDB)
        .filter_by(dataset_category_id=get_dataset_id(TRAIN_BUCKET))
        .offset(page.skip)
        .limit(page.limit)
        .all()
    )

    file = SpooledTemporaryFile()
    zip = zipfile.ZipFile(file, "w")
    for image in imagedb:
        errordb = (
            session.query(ErrorCategoryDB)
            .filter_by(id=image.metadata_rel.error_category_id)
            .first()
        )
        image_path = errordb.name + "/" + image.image_hash
        result = client.get_object(TRAIN_BUCKET, image_path)
        zip.writestr(TRAIN_BUCKET + "/" + image_path, result.data)
    zip.close()

    return file


@crud_exception_handle
def test_dataset_zip(page: Page):
    imagedb = (
        session.query(ImageDB)
        .join(MetadataDB)
        .filter_by(dataset_category_id=get_dataset_id(TEST_BUCKET))
        .offset(page.skip)
        .limit(page.limit)
        .all()
    )

    file = SpooledTemporaryFile()
    zip = zipfile.ZipFile(file, "w")
    for image in imagedb:
        errordb = (
            session.query(ErrorCategoryDB)
            .filter_by(id=image.metadata_rel.error_category_id)
            .first()
        )
        image_path = errordb.name + "/" + image.image_hash
        result = client.get_object(TEST_BUCKET, image_path)
        zip.writestr(TEST_BUCKET + "/" + image_path, result.data)
    zip.close()

    return file


@crud_exception_handle
def dataset_gen():
    pass
