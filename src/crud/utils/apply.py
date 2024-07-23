from pymongo.cursor import Cursor
from crud.exceptions import LimitValueError, InvalidSortOption, NonExistantColumn
from pymongo import ASCENDING, DESCENDING


def apply(
    cursor: Cursor,
    limit: int = 0,
    skip: int = 0,
    sort: str = "_id_",
    order: str | int = ASCENDING,
):
    """
    Applies sorting, limiting, and skipping operations on a cursor object.

    Args:
        cursor (Cursor): The cursor object to apply operations on.
        limit (int, optional): The maximum number of documents to return. Defaults to 0 (no limit).
        skip (int, optional): The number of documents to skip. Defaults to 0 (no skipping).
        sort (str, optional): The field to sort the documents by. Defaults to "_id_".
        order (str | int, optional): The sort order. Can be either "asc", "desc", or ASCENDING/DESCENDING constants. Defaults to ASCENDING.

    Returns:
        Cursor: The modified cursor object with applied operations.
    
    Raises:
        LimitValueError: If the limit value is negative.
        InvalidSortOption: If the sort option is not valid.
        NonExistantColumn: If the sort field does not exist in the collection's index information.
    """
    
    if limit < 0:
        raise LimitValueError(limit)

    if order not in [ASCENDING, DESCENDING]:
        if order == "asc":
            order = ASCENDING
        elif order == "desc":
            order = DESCENDING
        else:
            raise InvalidSortOption(order)

    return cursor.sort("_id", order).limit(limit).skip(skip)
