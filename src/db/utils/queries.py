from db.session import session
from db.model import DatasetCategoryDB, ErrorCategoryDB


def get_error_id(error: str) -> int:
    return session.query(ErrorCategoryDB).filter_by(name=error).first().id


def get_dataset_id(dataset: str) -> int:
    return session.query(DatasetCategoryDB).filter_by(name=dataset).first().id
