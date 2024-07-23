from fastapi import UploadFile
import crud.image
from db.session import session
from api.model.image import Image, ImageSchema
from db.model import ImageDB
from db.minio import client, PRODUCTIVE_BUCKET
import io


def add_image(image: UploadFile):
    client.put_object(
        PRODUCTIVE_BUCKET,
        image.filename,
        image.file,
        length=-1,
        part_size=10 * 1024 * 1024,
        content_type=image.content_type,
    )
