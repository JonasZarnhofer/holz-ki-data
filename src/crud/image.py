from api.model.metadata import Metadata, MetadataInternal, MetadataSchema
from api.model.page import Page

from fastapi import UploadFile

import sqlalchemy
import sqlalchemy.exc

from db.session import session
from db.model import (
    AnnotationDB,
    ImageDB,
    MetadataDB,
    ErrorCategoryDB,
    DatasetCategoryDB,
    BBoxDB,
    SegmentationDB,
    SegmentationPointDB,
)
from db.minio import client, PRODUCTIVE_BUCKET
from db.utils.enum import DATASET_CATEGORIES_DB_NONE, ERROR_CATEGORIES_DB_NONE

from crud.utils.queries import get_error_id, get_dataset_id
from crud.utils.rollback import crud_exception_handle
from crud.utils.hash import hash_file

from categories import ERROR_CATEGORIES, TRAIN, TEST
from minio.helpers import ObjectWriteResult

import zipfile
from tempfile import SpooledTemporaryFile


def image_exists(image_hash: str) -> bool:
    return session.query(ImageDB).filter_by(image_hash=image_hash).first() is not None


def _create_image_zip(imagedb: ImageDB) -> SpooledTemporaryFile:
    file = SpooledTemporaryFile()
    zip = zipfile.ZipFile(file, "w")
    for image in imagedb:
        errordb = (
            session.query(ErrorCategoryDB)
            .filter_by(id=image.metadata_rel.error_category_id)
            .first()
        )
        image_path = image.image_hash
        result = client.get_object(PRODUCTIVE_BUCKET, image_path)
        zip.writestr(errordb.name + "/" + image_path, result.data)
    zip.close()

    return file


@crud_exception_handle
async def _add_image(
    image: UploadFile,
    metadata: Metadata,
    dataset_type: str = DATASET_CATEGORIES_DB_NONE,
    bucket: str = PRODUCTIVE_BUCKET,
) -> ObjectWriteResult:
    # Hashing the image to get a unique identifier. Additionally
    # this prevents the same image from being uploaded multiple times.
    # Special image hashing algorithms (a-hash, p-hash) might be able to improve this.
    image_hash = hash_file(image.file)
    await image.seek(0)

    if session.query(ImageDB).filter_by(image_hash=image_hash).first() is not None:
        raise ValueError("Image already exists.")

    if dataset_type not in ERROR_CATEGORIES:
        raise ValueError(f"Category must be in {ERROR_CATEGORIES}.")

    if len(metadata.annotations) == 0:
        raise ValueError("Image has not been annotated yet")

    metadatadb = MetadataDB(
        metadata.width,
        metadata.height,
        get_dataset_id(dataset_type),
        metadata.capture_datetime,
    )
    session.add(metadatadb)
    session.flush()

    ids = set([id[0] for id in session.query(ErrorCategoryDB.id).all()])
    print(f"ids: {ids}")
    for annotation in metadata.annotations:
        if annotation.category_id not in ids:
            raise ValueError(f"Annotation must be in {ERROR_CATEGORIES}.")

        annotationdb = AnnotationDB(annotation.category_id, metadatadb.id)
        session.add(annotationdb)
        session.flush()

        bbox = annotation.bbox
        session.add(
            BBoxDB(
                x=bbox.x,
                y=bbox.y,
                width=bbox.width,
                height=bbox.height,
                annotation_id=annotationdb.id,
            )
        )
        session.flush()

        segmentations = annotation.segmentation
        segmentationsdb = SegmentationDB(annotationdb.id)
        session.add(segmentationsdb)
        session.flush()

        for segmentation in segmentations:
            session.add(
                SegmentationPointDB(
                    x=segmentation.x,
                    y=segmentation.y,
                    segmentation_id=segmentationsdb.id,
                )
            )
        session.flush()

    imagedb = ImageDB(image_hash=image_hash, metadata_id=metadatadb.id)
    session.add(imagedb)

    await image.seek(0)
    try:
        result = client.put_object(
            bucket,
            image_hash,
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


@crud_exception_handle
async def add_image(image: UploadFile, metadata: Metadata) -> ObjectWriteResult:
    metadata_internal = MetadataInternal(
        **metadata.model_dump(),
        dataset_type=DATASET_CATEGORIES_DB_NONE,
        error_type=ERROR_CATEGORIES_DB_NONE,
    )
    return await _add_image(image, metadata_internal)


@crud_exception_handle
async def add_train_image(
    image: UploadFile, dataset_type: str, metadata: Metadata
) -> ObjectWriteResult:
    return await _add_image(image, metadata, dataset_type)


@crud_exception_handle
async def add_test_image(
    image: UploadFile, dataset_type: str, metadata: Metadata
) -> ObjectWriteResult:
    return await _add_image(image, metadata, dataset_type)


@crud_exception_handle
def unlabeld_zip(page: Page) -> SpooledTemporaryFile:
    imagedb = (
        session.query(ImageDB)
        .join(MetadataDB)
        .filter_by(dataset_category_id=get_dataset_id(DATASET_CATEGORIES_DB_NONE))
        .offset(page.skip)
        .limit(page.limit)
        .all()
    )

    file = SpooledTemporaryFile()
    zip = zipfile.ZipFile(file, "w")
    for image in imagedb:
        image_path = image.image_hash
        result = client.get_object(PRODUCTIVE_BUCKET, image_path)
        zip.writestr(image_path, result.data)
    zip.close()

    return file


@crud_exception_handle
def train_dataset_zip(page: Page) -> SpooledTemporaryFile:
    imagedb = (
        session.query(ImageDB)
        .join(MetadataDB)
        .filter_by(dataset_category_id=get_dataset_id(TRAIN))
        .offset(page.skip)
        .limit(page.limit)
        .all()
    )

    file = _create_image_zip(imagedb)

    return file


@crud_exception_handle
def test_dataset_zip(page: Page):
    imagedb = (
        session.query(ImageDB)
        .join(MetadataDB)
        .filter_by(dataset_category_id=get_dataset_id(TEST))
        .offset(page.skip)
        .limit(page.limit)
        .all()
    )

    file = _create_image_zip(imagedb)

    return file


@crud_exception_handle
def train_image(image_name: str) -> SpooledTemporaryFile:
    image = (
        session.query(ImageDB)
        .filter_by(image_hash=image_name)
        .join(MetadataDB)
        .filter_by(dataset_category_id=get_dataset_id(TRAIN))
        .first()
    )
    if image is None:
        raise ValueError("Image not found.")

    data = client.get_object(PRODUCTIVE_BUCKET, image_name).data
    file = SpooledTemporaryFile()
    file.write(data)
    return file


@crud_exception_handle
def test_image(image_name: str) -> SpooledTemporaryFile:
    image = (
        session.query(ImageDB)
        .filter_by(image_hash=image_name)
        .join(MetadataDB)
        .filter_by(dataset_category_id=get_dataset_id(TEST))
        .first()
    )
    if image is None:
        raise ValueError("Image not found.")

    data = client.get_object(PRODUCTIVE_BUCKET, image_name).data
    file = SpooledTemporaryFile()
    file.write(data)
    return file
