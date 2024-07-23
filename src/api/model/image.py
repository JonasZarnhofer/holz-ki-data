from pydantic import BaseModel


class Image(BaseModel):
    name: str
    url: str


class ImageSchema(Image):
    id: int
