from db.session import users, roles
from api.model.user import User


def authenticate_user(username: str, password: str):
    return users.find_one({"name": username, "password": password})


def get_user_by_email(email: str):
    return users.find_one({"email": email})


def insert_user(user: User):
    result =  users.insert_one(user.model_dump())
