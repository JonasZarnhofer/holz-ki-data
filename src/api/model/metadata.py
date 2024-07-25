from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Metadata(BaseModel):
    capture_datetime: Optional[datetime | None] = None


class MetadataSchema(Metadata):
    id: int
