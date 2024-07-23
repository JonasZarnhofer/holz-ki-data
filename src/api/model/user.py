from api.model.model import MongoModel
from bson.objectid import ObjectId
from typing import List
from typing import Annotated
from pydantic.functional_validators import AfterValidator
from utils.validation import validate_objectid

class User(MongoModel):
    name: str
    email: str


class UserSchema(User):
    _id: Annotated[str, AfterValidator(validate_objectid)]
    client_id: Annotated[str, AfterValidator(validate_objectid)]
    roles: List[Annotated[str, AfterValidator(validate_objectid)]]
    password: str
    active: bool
