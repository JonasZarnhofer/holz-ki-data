from typing import List, Union
from api.model.coco import Coco
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
    BBoxDB,
    SegmentationDB,
    SegmentationPointDB,
)
from db.minio import client, PRODUCTIVE_BUCKET
from db.utils.enum import (
    DATASET_CATEGORIES_DB,
    DATASET_CATEGORIES_DB_NONE,
    ERROR_CATEGORIES_DB_NONE,
)
from categories import DATASETS


from crud.utils.queries import get_error_id, get_dataset_id, create_annotations
from crud.utils.rollback import crud_exception_handle
from crud.utils.hash import hash_file

from categories import ERROR_CATEGORIES
from minio.helpers import ObjectWriteResult

import zipfile
from tempfile import SpooledTemporaryFile


def label_with_coco(dataset: str, coco: Coco):
    errors: dict[int, ErrorCategoryDB] = {}
    for category in coco.categories:
        error_db = (
            session.query(ErrorCategoryDB)
            .filter(ErrorCategoryDB.name == category.name)
            .one()
        )

        if error_db is None:
            raise ValueError(f"Error category '{category.name}' does not exist.")

        errors[category.id] = error_db

    for image in coco.images:
        annotations = [
            annotation
            for annotation in coco.annotations
            if annotation.image_id == image.id
        ]

        image_name = image.file_name.split(".")[0]
        label(image_name, dataset, annotations)


async def label(image: str, dataset: Union[str, int], annotations: List[AnnotationDB]):
    """
    Label an image with the given annotations.
    Args:
        image (str): The image hash.
        annotations (List[AnnotationDB]): A list of annotations.
    Raises:
        ValueError: If the image does not exist.
    Returns:
        None
    """
    if isinstance(dataset, str):
        if dataset not in DATASETS:
            raise ValueError(f"Dataset must be in {DATASETS}")

        dataset_id = get_dataset_id(dataset)
    elif isinstance(dataset, int):
        if (
            session.query(DatasetCategoryDB)
            .filter(DatasetCategoryDB.id == dataset)
            .one()
            is None
        ):
            raise ValueError(f"Dataset with id '{dataset}' does not exist.")
        dataset_id = dataset

    metadata_db = (
        session.query(MetadataDB)
        .join(ImageDB)
        .filter(ImageDB.image_hash == image)
        .one()
    )

    if metadata_db is None:
        raise ValueError(f"Image {image} does not exist.")

    metadata_db.dataset_category_id = dataset_id

    create_annotations(metadata_db, annotations)


async def update_label(image: str, dataset: str):
    """
    Update the label of an image in the database. Already annotaded images cannot be 'unlabeled', tying to do so will therefore raise an error.
    Args:
        image (str): The image hash.
        dataset (str): The dataset category.
    Raises:
        ValueError: If the dataset does not exist or the image does not exist.
        ValueError: When trying to update an already labeled images to 'unlabeled'.
    Returns:
        MetadataDB: The updated metadata object.
    """

    if dataset not in DATASET_CATEGORIES_DB:
        raise ValueError(f"Dataset {dataset} does not exist.")

    metadata_db = (
        session.query(MetadataDB)
        .join(ImageDB)
        .filter(ImageDB.image_hash == image)
        .one()
    )

    if metadata_db is None:
        raise ValueError(f"Image {image} does not exist.")

    dataset_id = get_dataset_id(dataset)
    if metadata_db.dataset_category_id is dataset_id:
        if dataset is ERROR_CATEGORIES_DB_NONE:
            raise ValueError(
                f"Image {image} is already labeled and Annotates. Annotaded images cannot be 'unlabeled'. Remove the images Annotations first."
            )
        return

    metadata_db.dataset_category_id = dataset_id
    session.commit()

    return metadata_db
