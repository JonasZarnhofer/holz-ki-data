from typing import List, Optional
from pydantic import BaseModel
from api.model.annotations import Annotation


class ImageMetadata(BaseModel):
    width: int
    height: int
    file_name: str
    annotations: List[Annotation]


class Dataset(BaseModel):
    images: List[ImageMetadata]
