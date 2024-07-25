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
    metadata_rel = relationship("MetadataDB", back_populates="image", cascade="all, delete-orphan", single_parent=True)

    def __init__(self, image_hash, metadata_id):
        self.image_hash = image_hash
        self.metadata_id = metadata_id


class MetadataDB(Base):
    __tablename__ = "metadata"

    id = Column(Integer, primary_key=True)
    capture_datetime = Column(DateTime, nullable=True)
    image = relationship("ImageDB", back_populates="metadata_rel")

    def __init__(self, capture_datetime=None):
        self.capture_datetime = capture_datetime


Base.metadata.create_all(engine)
