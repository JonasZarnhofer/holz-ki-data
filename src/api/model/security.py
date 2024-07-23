from api.model.model import MongoModel
from typing import Optional


class Token(MongoModel):
    access_token: str
    token_type: str


class OAuth2Form(MongoModel):
    grant_type: Optional[str] = ""
    username: str
    password: str
    scope: Optional[str] = ""
    client_id: Optional[str] = ""
    client_secret: Optional[str] = ""
