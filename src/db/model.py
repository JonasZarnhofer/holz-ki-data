from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Table
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
    email = Column(String(50), unique=True, nullable=False)
    metadata_id = Column(Integer, ForeignKey("metadata.id"))


class MetadataDB(Base):
    __tablename__ = "metadata"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    deadline = Column(DateTime, nullable=False)


Base.metadata.create_all(engine)
