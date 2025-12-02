from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..db.database import Base

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

    images = relationship("Image", back_populates="project")

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))

    event = relationship("Event", back_populates="images")
    project = relationship("Project", back_populates="images")

class GroupInfo(Base):
    __tablename__ = "group_info"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    contact = Column(String)
