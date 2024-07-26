from typing import Annotated

from fastapi import APIRouter, HTTPException, UploadFile, status, Depends
from fastapi.responses import StreamingResponse

from api.model.metadata import Metadata, MetadataInternal, MetadataSchema
from api.model.page import Page

import crud
import crud.image
from crud.utils.streaming import stream_file

from db.minio import client
from db.minio import PRODUCTIVE_BUCKET, TRAIN_BUCKET, TEST_BUCKET

router = APIRouter(prefix="/image", tags=["Image"])


@router.post("", status_code=201)
async def add_image(image: UploadFile, metadata: Metadata = Depends()):
    if image.content_type != "image/jpeg":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File must be a jpeg image",
        )

    crud.image.add_image(image)


@router.post("/train/{category}", status_code=201)
async def add_image_with_category(
    image: UploadFile, category: str, metadata: Metadata = Depends()
):
    if image.content_type != "image/jpeg":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File must be a jpeg image",
        )

    internal_metadata = MetadataInternal(
        **metadata.model_dump(), dataset_type="train", error_type=category
    )

    try:
        await crud.image.add_train_image(image, category, internal_metadata)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/test/{category}", status_code=201)
async def add_image_with_category(
    image: UploadFile, category: str, metadata: Metadata = Depends()
):
    if image.content_type != "image/jpeg":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File must be a jpeg image",
        )

    internal_metadata = MetadataInternal(
        **metadata.model_dump(), dataset_type="test", error_type=category
    )

    try:
        await crud.image.add_test_image(image, category, internal_metadata)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/train", response_class=StreamingResponse)
async def get_train_dataset(page: Page = Depends()):
    file = crud.image.train_dataset_zip(page)
    file.seek(0)

    return StreamingResponse(content=stream_file(file), media_type="application/zip")


@router.get("/test", response_class=StreamingResponse)
async def get_test_dataset(page: Page = Depends()):
    file = crud.image.test_dataset_zip(page)
    file.seek(0)

    return StreamingResponse(content=stream_file(file), media_type="application/zip")
