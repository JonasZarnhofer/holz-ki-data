from tempfile import SpooledTemporaryFile
from typing import List
from api.model.coco import ImageMetadata
from api.model.annotations import Annotation
from api.model.coco import Coco, Category

from db.session import session
from db.model import (
    ImageDB,
    MetadataDB,
    ErrorCategoryDB,
    DatasetCategoryDB,
    AnnotationDB,
    SegmentationPointDB,
    SegmentationDB,
    BBoxDB,
)
from db.minio import client, PRODUCTIVE_BUCKET
from db.utils.enum import DATASET_CATEGORIES_DB_NONE, ERROR_CATEGORIES_DB_NONE
from crud.utils.queries import get_dataset_id
from categories import DATASETS, ERROR_CATEGORIES


def _get_coco(dataset: str, size: int = 0) -> Coco:
    if dataset not in DATASETS:
        raise ValueError(f"Dataset must be in {DATASETS}")

    if size == 0:
        images = session.query(ImageDB).all()
    else:
        images = session.query(ImageDB).limit(size).all()

    images_coco = []
    for image in images:
        coco_set = (
            session.query(ImageDB, MetadataDB).filter(
                ImageDB.id == image.id,
                MetadataDB.id == ImageDB.id,
                MetadataDB.dataset_category_id == get_dataset_id(dataset),
                MetadataDB.id == AnnotationDB.metadata_id,
            )
        ).all()

        annotations_coco = []
        for image, metadata in coco_set:
            images_coco.append(
                ImageMetadata(
                    id=image.id,
                    width=metadata.width,
                    height=metadata.height,
                    file_name=image.image_hash + ".jpg",
                )
            )

            annotations = (
                session.query(AnnotationDB)
                .filter(AnnotationDB.metadata_id == metadata.id)
                .all()
            )

            for annotation in annotations:
                segmentations = (
                    session.query(SegmentationDB)
                    .filter(SegmentationDB.annotation_id == annotation.id)
                    .all()
                )
                bbox = (
                    session.query(BBoxDB)
                    .filter(BBoxDB.annotation_id == annotation.id)
                    .first()
                )
                bbox_coco = [bbox.x, bbox.y, bbox.width, bbox.height]

                segmentations_coco = []

                for segmentation in segmentations:
                    segmentation_points = (
                        session.query(SegmentationPointDB)
                        .filter(SegmentationPointDB.segmentation_id == segmentation.id)
                        .all()
                    )

                    coords = []
                    for point in segmentation_points:
                        coords.append(point.x)
                        coords.append(point.y)
                    segmentations_coco.append(coords)

                annotations_coco.append(
                    Annotation(
                        id=annotation.id,
                        image_id=image.id,
                        segmentation=segmentations_coco,
                        category_id=annotation.error_category_id,
                        bbox=bbox_coco,
                    )
                )

    categories_db = session.query(ErrorCategoryDB).all()
    categories_coco = [
        Category(id=category_db.id, name=category_db.name)
        for category_db in categories_db
    ]

    coco = Coco(
        images=images_coco, annotations=annotations_coco, categories=categories_coco
    )

    return coco


def get_dataset_coco_file(dataset: str, size: int) -> SpooledTemporaryFile:
    coco = _get_coco(dataset, size)

    file = SpooledTemporaryFile(mode="w")
    file.write(coco.model_dump_json())
    return file
