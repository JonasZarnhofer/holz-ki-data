from typing import Annotated, Union

from fastapi import APIRouter, HTTPException, UploadFile, status, Depends
from fastapi.responses import StreamingResponse

from api.model.metadata import Metadata, MetadataInternal, MetadataSchema
from api.model.page import Page
from api.model.dataset import Dataset

import crud
import crud.image
import crud.label
from crud.utils.queries import get_error
from crud.utils.streaming import stream_file


from db.minio import client
from db.utils.enum import DATASET_CATEGORIES_DB_NONE, ERROR_CATEGORIES_DB_NONE

from categories import DATASETS, ERROR_CATEGORIES

router = APIRouter(prefix="/label", tags=["Labeling"])


@router.post("/{image}", status_code=201)
async def label_image(dataset: str, category: Union[str, int], image: str):
    if isinstance(category, int):
        category = get_error(category)

    if dataset not in DATASETS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image must be either of {DATASETS}",
        )

    if category not in ERROR_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category must be one of {ERROR_CATEGORIES}",
        )

    if not crud.image.image_exists(image):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image {image} not found",
        )

    try:
        await crud.label.label(dataset, category, image)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
