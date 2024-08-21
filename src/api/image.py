from typing import Annotated
from fastapi import APIRouter, HTTPException, UploadFile, status, Depends, Form, File
from fastapi.responses import StreamingResponse

from api.model.metadata import (
    Metadata,
    MetadataInternal,
    MetadataSchema,
    MetadataUnlabeled,
)
from api.model.page import Page

import crud
import crud.image
from crud.utils.streaming import stream_file

from categories import DATASETS

router = APIRouter(prefix="/image", tags=["Image"])


@router.post("", status_code=201)
async def add_image(
    image: Annotated[UploadFile, File()],
    metadata: Annotated[MetadataUnlabeled, Form()],
):
    if image.content_type != "image/jpeg":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File must be a jpeg image",
        )

    await crud.image.add_image(image, metadata)


@router.post("/{dataset_type}/{category}", status_code=201)
async def add_image_with_category(
    image: UploadFile, category: str, dataset_type: str, metadata: Metadata = Depends()
):
    if dataset_type not in DATASETS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dataset type must be in {DATASETS}",
        )

    if image.content_type != "image/jpeg":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File must be a jpeg image",
        )

    try:
        await crud.image.add_test_image(image, dataset_type, metadata)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("", status_code=200, response_class=StreamingResponse)
async def get_unlabeld_image(page: Page = Depends()):
    file = crud.image.unlabeld_zip(page)
    file.seek(0)

    return StreamingResponse(content=stream_file(file), media_type="application/zip")


@router.get("/train", response_class=StreamingResponse)
async def get_train_dataset(page: Page = Depends()):
    file = crud.image.train_dataset_zip(page)
    file.seek(0)

    return StreamingResponse(content=stream_file(file), media_type="application/zip")


@router.get("/train/{image}", response_class=StreamingResponse)
async def get_train_image(image: str):
    file = crud.image.train_image(image)
    file.seek(0)

    return StreamingResponse(content=stream_file(file), media_type="image/jpeg")


@router.get("/test", response_class=StreamingResponse)
async def get_test_dataset(page: Page = Depends()):
    file = crud.image.test_dataset_zip(page)
    file.seek(0)

    return StreamingResponse(content=stream_file(file), media_type="application/zip")


@router.get("/test/{image}", response_class=StreamingResponse)
async def get_test_dataset(image: str):
    file = crud.image.test_image(image)
    file.seek(0)

    return StreamingResponse(content=stream_file(file), media_type="image/jpeg")
