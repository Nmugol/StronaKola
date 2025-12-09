import enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from ..db.database import Base


class Platforms(str, enum.Enum):
    WIN = "Windows"
    LINUX = "Linux"
    MACOS = "MacOS"


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    date = Column(DateTime)
    description = Column(String)

    images = relationship("Image", back_populates="event")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    technologies = Column(String)
    year = Column(Integer, nullable=True)

    images = relationship("Image", back_populates="project")
    executable = relationship("ExecutableFile", back_populates="project")
    files = relationship("ProjectFiles", back_populates="project")


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    event = relationship("Event", back_populates="images")
    project = relationship("Project", back_populates="images")


class GroupInfo(Base):
    __tablename__ = "group_info"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    contact = Column(String)


class ExecutableFile(Base):
    __tablename__ = "executable_file"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, index=True)
    version = Column(String)
    platform = Column(SAEnum(Platforms))
    project_id = Column(Integer, ForeignKey("projects.id"))

    project = relationship("Project", back_populates="executable")


class ProjectFiles(Base):
    __tablename__ = "project_files"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))

    project = relationship("Project", back_populates="files")
