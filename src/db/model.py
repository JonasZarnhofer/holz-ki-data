from datetime import datetime
from typing import List
from sqlalchemy import (
    Column,
    Integer,
    String,
    Double,
    Boolean,
    ForeignKey,
    DateTime,
    Table,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.orm import declarative_base

from db.session import engine, session

Base = declarative_base()


# association table for the MetadataDB and AnnotationDB many-to-many relationship
metadata_annotation = Table(
    "metadata_annotation",
    Base.metadata,
    Column("metadata_id", ForeignKey("metadata.id")),
    Column("annotation_id", ForeignKey("annotation.id")),
)


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


class SegmentationPointDB(Base):
    __tablename__ = "point"

    id = Column(Integer, primary_key=True)
    x = Column(Double, nullable=False)
    y = Column(Double, nullable=False)
    segmentation_id: Mapped[int] = mapped_column(
        ForeignKey("segmentation.id"), nullable=False
    )

    def __init__(self, x, y, segmentation_id):
        self.x = x
        self.y = y
        self.segmentation_id = segmentation_id


class SegmentationDB(Base):
    __tablename__ = "segmentation"

    id = Column(Integer, primary_key=True)
    annotation_id: Mapped[int] = mapped_column(
        ForeignKey("annotation.id"), nullable=False
    )

    annotation: Mapped["AnnotationDB"] = relationship(
        single_parent=True,
    )

    points: Mapped[List[SegmentationPointDB]] = relationship(
        cascade="all",
    )

    def __init__(self, annotation_id):
        self.annotation_id = annotation_id


class BBoxDB(Base):
    __tablename__ = "bbox"

    id = Column(Integer, primary_key=True)
    x = Column(Double, nullable=False)
    y = Column(Double, nullable=False)
    width = Column(Double, nullable=False)
    height = Column(Double, nullable=False)

    annotation_id: Mapped[int] = mapped_column(
        ForeignKey("annotation.id"), nullable=False
    )

    annotation: Mapped["AnnotationDB"] = relationship(
        single_parent=True,
    )

    def __init__(self, x, y, width, height, annotation_id):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.annotation_id = annotation_id


class ErrorCategoryDB(Base):
    __tablename__ = "error_category"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name


class AnnotationDB(Base):
    __tablename__ = "annotation"

    id = Column(Integer, primary_key=True)
    error_category_id: Mapped[int] = mapped_column(
        ForeignKey("error_category.id"), nullable=False
    )
    metadata_id: Mapped[int] = mapped_column(ForeignKey("metadata.id"), nullable=False)

    error_category: Mapped[ErrorCategoryDB] = relationship(
        cascade="all",
    )
    metadata_rel: Mapped["MetadataDB"] = relationship(
        cascade="all",
    )

    def __init__(self, error_category_id, metadata_id):
        self.error_category_id = error_category_id
        self.metadata_id = metadata_id


class MetadataDB(Base):
    __tablename__ = "metadata"

    id = Column(Integer, primary_key=True)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    capture_datetime = Column(DateTime, nullable=True)

    dataset_category_id = Column(ForeignKey("dataset_category.id"), nullable=False)

    annotations: Mapped[List[AnnotationDB]] = relationship(
        secondary=metadata_annotation
    )

    dataset_category = relationship(
        "DatasetCategoryDB",
        back_populates="metadata_rel",
        cascade="all, delete-orphan",
        single_parent=True,
    )

    image = relationship("ImageDB", back_populates="metadata_rel", uselist=False)

    def __init__(
        self,
        width: int,
        height: int,
        dataset_category_id: int,
        capture_datetime=datetime | None,
    ):
        self.width = width
        self.height = height
        self.capture_datetime = capture_datetime
        self.dataset_category_id = dataset_category_id


class DatasetCategoryDB(Base):
    __tablename__ = "dataset_category"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    metadata_rel = relationship(
        "MetadataDB", back_populates="dataset_category", uselist=False
    )

    def __init__(self, name):
        self.name = name


Base.metadata.create_all(engine)

from db.utils.populate import populate

populate()
