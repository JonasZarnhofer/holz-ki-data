import sqlalchemy
from db.model import DatasetCategoryDB, ErrorCategoryDB
from db.session import session
from db.utils.enum import DATASET_CATEGORIES_DB, ERROR_CATEGORIES_DB




def populate_dataset_categories():
    try:
        for cat in DATASET_CATEGORIES_DB:
            if session.query(DatasetCategoryDB).filter_by(name=cat).first() == None:
                session.add(DatasetCategoryDB(cat))
    except Exception as e:
        session.rollback()
        raise e
    else:
        session.commit()


def populate_error_categories():
    try:
        for cat in ERROR_CATEGORIES_DB:
            if session.query(ErrorCategoryDB).filter_by(name=cat).first() == None:
                session.add(ErrorCategoryDB(cat))
    except Exception as e:
        session.rollback()
        raise e
    else:
        session.commit()


def populate():
    populate_dataset_categories()
    populate_error_categories()
