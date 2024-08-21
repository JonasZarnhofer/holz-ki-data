from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from api.model.annotations import Annotation


class MetadataUnlabeled(BaseModel):
    capture_datetime: Optional[datetime | None] = None
    width: int
    height: int


class Metadata(MetadataUnlabeled):
    annotations: List[Annotation]


class MetadataSchema(Metadata):
    dataset_type: str


class MetadataInternal(MetadataSchema):
    id: int
