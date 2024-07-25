from typing import Annotated
from fastapi import APIRouter, HTTPException, UploadFile, status, Depends
from api.model.metadata import Metadata, MetadataSchema
import crud.image
from db.minio import client
import crud
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

    try:
        crud.image.add_train_image(image, category, metadata)
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

    try:
        crud.image.add_test_image(image, category, metadata)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
