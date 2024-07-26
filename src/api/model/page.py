from pydantic import BaseModel


class Page(BaseModel):
    skip: int
    limit: int
