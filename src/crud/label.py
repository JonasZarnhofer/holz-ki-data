from api.model.metadata import Metadata, MetadataInternal, MetadataSchema
from api.model.page import Page

from fastapi import UploadFile

import sqlalchemy
import sqlalchemy.exc

from db.session import session
from db.model import (
    ImageDB,
    MetadataDB,
    ErrorCategoryDB,
    DatasetCategoryDB,
    AnnotationDB,
)
from db.minio import client, PRODUCTIVE_BUCKET
from db.utils.enum import DATASET_CATEGORIES_DB_NONE, ERROR_CATEGORIES_DB_NONE

from crud.utils.queries import get_error_id, get_dataset_id
from crud.utils.rollback import crud_exception_handle
from crud.utils.hash import hash_file

from categories import ERROR_CATEGORIES
from minio.helpers import ObjectWriteResult

import zipfile
from tempfile import SpooledTemporaryFile


async def label(dataset: str, category: str, image_hash: str):
    metadata = (
        session.query(MetadataDB)
        .join(ImageDB)
        .filter(ImageDB.image_hash == image_hash)
        .one()
    )

    annotation_count = (
        session.query(AnnotationDB).filter_by(metadata_id=metadata.id).count()
    )
    if annotation_count == 0:
        raise ValueError("Image has not been annotated yet")

    metadata.error_category_id = get_error_id(category)
    metadata.dataset_category_id = get_dataset_id(dataset)
    session.commit()
