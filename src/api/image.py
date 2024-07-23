from typing import Annotated
from fastapi import APIRouter, HTTPException, UploadFile, status
from api.model.image import Image, ImageSchema
import crud.image
from db.minio import client
import crud

router = APIRouter(prefix="/image", tags=["Image"])


@router.post("", status_code=201)
async def add_image(image: UploadFile):
    if image.content_type != "image/jpeg":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File must be a jpeg image",
        )
    
    crud.image.add_image(image)
