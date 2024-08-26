from typing import Annotated, List

from fastapi import APIRouter, HTTPException, UploadFile, Depends, status
from fastapi.responses import StreamingResponse, FileResponse, Response

from api.model.metadata import Metadata, MetadataInternal, MetadataSchema
from api.model.coco import ImageMetadata
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


@router.get("/{dataset}")
async def get_dataset(dataset: str, size: int = 10):
    try:
        file = crud.dataset.get_dataset_coco_file(dataset, size)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    file.seek(0)
    return Response(file.read(), media_type="application/json")
