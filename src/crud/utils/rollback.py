from sqlalchemy.exc import (
    SQLAlchemyError,
)
from db.session import session
from fastapi import HTTPException, status


def crud_exception_handle(crud_func):
    def wrapper(*args, **kwargs):
        try:
            return crud_func(*args, **kwargs)
        except SQLAlchemyError as e:
            session.rollback()
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error",
            )

    return wrapper
