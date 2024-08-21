from db.session import session
from db.model import DatasetCategoryDB, ErrorCategoryDB


def get_error_id(error: str) -> int:
    return session.query(ErrorCategoryDB).filter_by(name=error).first().id


def get_error(error_id: int) -> str:
    return session.query(ErrorCategoryDB).filter_by(id=error_id).first().name


def get_dataset_id(dataset: str) -> int:
    return session.query(DatasetCategoryDB).filter_by(name=dataset).first().id


def get_dataset(id: int) -> str:
    return session.query(DatasetCategoryDB).filter_by(id=id).first().name
