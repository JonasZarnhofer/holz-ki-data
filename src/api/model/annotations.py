from pydantic import BaseModel
from typing import List, Optional


class BBox(BaseModel):
    x: float
    y: float
    width: float
    height: float


class Annotation(BaseModel):
    id: int
    image_id: int
    category_id: int
    bbox: List[float]
    segmentation: List[List[float]]


class AnnotationInteral(Annotation):
    bbox_mode: Optional[str] = None


class AnnotationSchema(Annotation):
    id: int
