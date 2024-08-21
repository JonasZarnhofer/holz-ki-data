from typing import Annotated, List

from fastapi import APIRouter, HTTPException, UploadFile, status, Depends
from fastapi.responses import StreamingResponse

from api.model.metadata import Metadata, MetadataInternal, MetadataSchema
from api.model.dataset import ImageMetadata
from api.model.page import Page

import crud
import crud.dataset
import crud.image
import crud.label
from crud.utils.streaming import stream_file

from db.minio import client
from db.utils.enum import DATASET_CATEGORIES_DB_NONE, ERROR_CATEGORIES_DB_NONE

from categories import DATASETS, ERROR_CATEGORIES


router = APIRouter(prefix="/dataset", tags=["Dataset"])


@router.get("/{dataset}", response_model=List[ImageMetadata])
async def get_dataset(dataset: str, size: int = 10):
    try:
        dataset = crud.dataset.get_dataset(dataset, size)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return dataset
