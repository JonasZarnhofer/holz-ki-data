from typing import Annotated
from fastapi import APIRouter, HTTPException, UploadFile, status, Depends, Form, File
from fastapi.responses import StreamingResponse, Response

from api.model.metadata import (
    Metadata,
    MetadataInternal,
    MetadataSchema,
    MetadataUnlabeled,
)
from api.model.page import Page
from api.model.coco import Coco

import crud
import crud.image
from crud.utils.streaming import stream_file

from categories import DATASETS
from db.utils.enum import DATASET_CATEGORIES_DB_NONE, ERROR_CATEGORIES_DB_NONE

router = APIRouter(prefix="/image", tags=["Image"])


# Due to limitations of FastAPI regarding Pydantic models in multipart form data,
# the metadata is passed as query parameters instead of form data.
# This way swagger UI can document the endpoint correctly.
@router.post("", status_code=201)
async def add_image(
    image: Annotated[UploadFile, File()],
    metadata: MetadataUnlabeled = Depends(),
):
    """
    Add an image to the system.
    Parameters:
    - image: Annotated[UploadFile, File()]: The image file to be added.
    - metadata: MetadataUnlabeled: Additional metadata for the image.
    Raises:
    - HTTPException: If the file is not a jpeg image.
    Returns:
    - None
    """

    if image.content_type != "image/jpeg":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File must be a jpeg image",
        )

    await crud.image.add_image(image, metadata)


@router.post("/{dataset_type}/{category}", status_code=201)
async def add_image_with_category(
    image: Annotated[UploadFile, File(...)],
    metadata: Annotated[str, Form(...)],
    dataset_type: str,
):
    """
    Add an image with category to the dataset.
    Parameters:
        image (UploadFile): The image file to be added.
        metadata (str): The metadata associated with the image.
        dataset_type (str): The dataset.
    Raises:
        HTTPException: If the dataset type is not valid or the file is not a jpeg image.
    Returns:
        None
    """

    metadata = Metadata.model_validate_json(metadata)
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


@router.get("/{dataset}", response_class=Response)
async def get_train_dataset(dataset: str, page: Page = Depends()):
    file = crud.image.dataset_zip(page, dataset)

    file.seek(0)
    return Response(
        file.read(),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={dataset}.zip"},
    )


@router.get("/train/{image}", response_class=StreamingResponse)
async def get_train_image(image: str):
    file = crud.image.train_image(image)
    file.seek(0)

    return StreamingResponse(content=stream_file(file), media_type="image/jpeg")


@router.get("/test/{image}", response_class=StreamingResponse)
async def get_test_dataset(image: str):
    file = crud.image.test_image(image)
    file.seek(0)

    return StreamingResponse(content=stream_file(file), media_type="image/jpeg")
