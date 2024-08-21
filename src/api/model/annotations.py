from pydantic import BaseModel
from typing import List, Optional


class BBox(BaseModel):
    x: float
    y: float
    width: float
    height: float


class Annotation(BaseModel):
    category_id: int
    bbox: BBox
    segmentation: List[List[float]]


class AnnotationInteral(Annotation):
    bbox_mode: Optional[str] = None


class AnnotationSchema(Annotation):
    id: int
