from typing import Annotated
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from api.model.user import User, UserSchema
from api.model.security import Token

from security.oauth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from utils.security import hash
from crud import security


router = APIRouter()


@router.post("/token", status_code=200, tags=["Security"])
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """
    Authenticates the user and generates an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing the username and password.

    Returns:
        Token: The generated access token.

    Raises:
        HTTPException: If the username or password is incorrect.
    """

    user = security.authenticate_user(
        form_data.username, hash(form_data.password))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")


@router.post("/signup", status_code=201, tags=["Security"])
async def signup(user: User) -> UserSchema:
    """
    Sign up a new user.

    Args:
        user (User): The user object containing the user's information.

    Returns:
        UserSchema: The user object with additional schema information.

    Raises:
        HTTPException: If the user already exists.

    """
    hashed_password: str = hash(user.password)
    hashed = User(email=user.email, password=hashed_password,
                  username=user.username)

    user = await security.insert_user(hashed)
    if user == None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
