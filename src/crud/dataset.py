from typing import List
from api.model.dataset import ImageMetadata

from db.session import session
from db.model import ImageDB, MetadataDB, ErrorCategoryDB, DatasetCategoryDB
from db.minio import client, PRODUCTIVE_BUCKET
from db.utils.enum import DATASET_CATEGORIES_DB_NONE, ERROR_CATEGORIES_DB_NONE
from crud.utils.queries import get_dataset_id
from categories import DATASETS, ERROR_CATEGORIES


def _get_from_dataset(dataset: str, size: int = 0) -> List[str]:
    query = (
        session.query(ImageDB)
        .join(MetadataDB)
        .filter_by(dataset_category_id=get_dataset_id(dataset))
    )

    if size == 0:
        images = query.all()
    else:
        images = query.limit(size).all()

    return images


def get_dataset(dataset: str, size: int) -> List[ImageMetadata]:
    if dataset not in DATASETS:
        raise ValueError(f"Dataset must be in {DATASETS}")

    images = _get_from_dataset(dataset)
