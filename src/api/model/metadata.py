from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Metadata(BaseModel):
    capture_datetime: Optional[datetime | None] = None


class MetadataInternal(Metadata):
    dataset_type: str
    error_type: str


class MetadataSchema(MetadataInternal):
    id: int
