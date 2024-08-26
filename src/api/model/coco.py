from pydantic import BaseModel
from typing import List, Optional
from api.model.annotations import Annotation


class Category(BaseModel):
    id: int
    name: str


class ImageMetadata(BaseModel):
    id: int
    width: int
    height: int
    file_name: str


class Coco(BaseModel):
    info: Optional[dict] = {}
    images: List[ImageMetadata]
    annotations: List[Annotation]
    categories: Optional[List[Category]] = []
