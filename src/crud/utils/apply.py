from pymongo.cursor import Cursor
from crud.exceptions import LimitValueError, InvalidSortOption, NonExistantColumn
from pymongo import ASCENDING, DESCENDING


def apply(cursor: Cursor, limit: int = 0, skip: int = 0):
    pass
