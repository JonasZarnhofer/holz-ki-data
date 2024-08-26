from typing import Annotated, List, Union

from fastapi import APIRouter, File, HTTPException, UploadFile, status, Depends
from fastapi.responses import StreamingResponse

from api.model.metadata import Metadata, MetadataInternal, MetadataSchema
from api.model.annotations import Annotation
from api.model.page import Page
from api.model.coco import Coco

import crud
import crud.image
import crud.label
from crud.utils.queries import get_error
from crud.utils.streaming import stream_file


from db.minio import client
from db.utils.enum import DATASET_CATEGORIES_DB_NONE, ERROR_CATEGORIES_DB_NONE

from categories import DATASETS, ERROR_CATEGORIES

router = APIRouter(prefix="/label", tags=["Labeling"])


@router.post("/coco", status_code=201)
def label_with_coco(coco_json: Annotated[UploadFile, File()]):
    coco = Coco.model_validate_json(coco_json.file.read())


@router.post("/{image}", status_code=201)
async def label_image(
    image: str, dataset: Union[str, int], annotations: List[Annotation]
):
    """
    Labels an image with the provided dataset and annotations.
    Parameters:
    - image (str): The name of the image.
    - dataset (Union[str, int]): The dataset identifier or name to be used for labeling.
    - annotations (List[Annotation]): A list of annotations to be applied to the image.
    """

    try:
        await crud.label.label(image, dataset, annotations)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch("/{image}", status_code=201)
async def label_image(image: str, dataset: str):
    """
    Moves an image to another dataset.
    Args:
        image (str): The name of the image.
        dataset (str): The new dataset.
    Returns:
        MetadataDB: The updated metadata.
    """
    try:
        return await crud.label.update_label(image, dataset)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
