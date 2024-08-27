from db.session import session
from db.model import (
    MetadataDB,
    DatasetCategoryDB,
    ErrorCategoryDB,
    AnnotationDB,
    BBoxDB,
    SegmentationDB,
    SegmentationPointDB,
)

from typing import List
from api.model.annotations import Annotation

from logger import logger


def get_error_id(error: str) -> int:
    return session.query(ErrorCategoryDB).filter_by(name=error).first().id


def get_error(error_id: int) -> str:
    return session.query(ErrorCategoryDB).filter_by(id=error_id).first().name


def get_dataset_id(dataset: str) -> int:
    return session.query(DatasetCategoryDB).filter_by(name=dataset).first().id


def get_dataset(id: int) -> str:
    return session.query(DatasetCategoryDB).filter_by(id=id).first().name


def create_annotations(metadata: MetadataDB, annotations: List[Annotation]):
    try:
        annotation_dbs = []
        for annotation in annotations:
            annotation_db = AnnotationDB(
                metadata_id=metadata.id,
                error_category_id=annotation.category_id,
            )
            session.add(annotation_db)
            session.flush()

            bbox_db = BBoxDB(
                annotation_id=annotation_db.id,
                x=annotation.bbox[0],
                y=annotation.bbox[1],
                width=annotation.bbox[2],
                height=annotation.bbox[3],
            )
            session.add(bbox_db)

            if annotation.segmentation is not None:
                for segmentation in annotation.segmentation:
                    segmentation_db = SegmentationDB(
                        annotation_id=annotation_db.id,
                    )
                    session.add(segmentation_db)
                    session.flush()

                    print(f"seg: {segmentation}")
                    for i in range(0, len(segmentation), 2):
                        point_db = SegmentationPointDB(
                            segmentation_id=segmentation_db.id,
                            x=segmentation[i],
                            y=segmentation[i + 1],
                        )
                        session.add(point_db)

            annotation_dbs.append(annotation_db)

        session.flush()
    except Exception as e:
        logger.error(f"Error creating annotations: {e}")
        session.rollback()
        return []

    return annotation_dbs
