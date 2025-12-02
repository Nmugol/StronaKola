from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ImageBase(BaseModel):
    id: Optional[int] = None
    file_path: str

class ImageCreate(ImageBase):
    pass

class Image(ImageBase):
    id: int
    event_id: Optional[int] = None
    project_id: Optional[int] = None

    class Config:
        from_attributes = True

class EventBase(BaseModel):
    name: str
    date: datetime
    description: str

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: int
    images: List[Image] = []

    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    name: str
    description: str
    technologies: str

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    images: List[Image] = []

    class Config:
        from_attributes = True

class GroupInfoBase(BaseModel):
    description: str
    contact: str

class GroupInfoCreate(GroupInfoBase):
    pass

class GroupInfo(GroupInfoBase):
    id: int

    class Config:
        from_attributes = True
