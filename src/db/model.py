from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

from db.session import engine, session

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    active = Column(Boolean, nullable=False)

    def __init__(self, name):
        self.name = name
        self.active = True


class ImageDB(Base):
    __tablename__ = "image"

    id = Column(Integer, primary_key=True)
    image_hash = Column(String(256), unique=True, nullable=False)
    metadata_id = Column(Integer, ForeignKey("metadata.id"), unique=True, nullable=True)
    metadata_rel = relationship(
        "MetadataDB",
        back_populates="image",
        cascade="all, delete-orphan",
        single_parent=True,
    )

    def __init__(self, image_hash, metadata_id):
        self.image_hash = image_hash
        self.metadata_id = metadata_id


class MetadataDB(Base):
    __tablename__ = "metadata"

    id = Column(Integer, primary_key=True)
    capture_datetime = Column(DateTime, nullable=True)
    dataset_category_id = Column(ForeignKey("dataset_category.id"), nullable=False)
    error_category_id = Column(ForeignKey("error_category.id"), nullable=False)

    dataset_category = relationship(
        "DatasetCategoryDB",
        back_populates="metadata_rel",
        cascade="all, delete-orphan",
        single_parent=True,
    )

    error_category = relationship(
        "ErrorCategoryDB",
        back_populates="metadata_rel",
        cascade="all, delete-orphan",
        single_parent=True,
    )

    image = relationship("ImageDB", back_populates="metadata_rel", uselist=False)

    def __init__(self, capture_datetime, dataset_category_id, error_category_id):
        self.capture_datetime = capture_datetime
        self.dataset_category_id = dataset_category_id
        self.error_category_id = error_category_id


class DatasetCategoryDB(Base):
    __tablename__ = "dataset_category"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    metadata_rel = relationship(
        "MetadataDB", back_populates="dataset_category", uselist=False
    )

    def __init__(self, name):
        self.name = name


class ErrorCategoryDB(Base):
    __tablename__ = "error_category"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    metadata_rel = relationship(
        "MetadataDB", back_populates="error_category", uselist=False
    )

    def __init__(self, name):
        self.name = name


Base.metadata.create_all(engine)

from db.utils.populate import populate

populate()
