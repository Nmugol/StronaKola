from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.declarative import ConcreteBase

# 1. Definicja Enuma (musi być identyczna jak w models.py lub zaimportowana)


class Platforms(str, Enum):
    WIN = "Windows"
    LINUX = "Linux"
    MACOS = "MacOS"


# --- SCHEMATY DLA PLIKÓW PROJEKTOWYCH ---


class ProjectFilesBase(BaseModel):
    file_path: str


class ProjectFilesCreate(ProjectFilesBase):
    pass


class ProjectFiles(ProjectFilesBase):
    id: int
    project_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


# --- SCHEMATY DLA PLIKÓW WYKONYWALNYCH ---


class ExecutableFileBase(BaseModel):
    file_path: str
    version: str
    platform: Platforms  # Walidacja: przyjmie tylko wartości z Enuma


class ExecutableFileCreate(ExecutableFileBase):
    pass


class ExecutableFile(ExecutableFileBase):
    id: int
    project_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


# --- SCHEMATY DLA ZDJĘĆ ---


class ImageBase(BaseModel):
    file_path: str
    # Usunięto id z Base - przy tworzeniu (Create) jeszcze go nie mamy


class ImageCreate(ImageBase):
    pass


class Image(ImageBase):
    id: int
    event_id: Optional[int] = None
    project_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


# --- SCHEMATY DLA EVENTÓW ---


class EventBase(BaseModel):
    name: str
    date: datetime
    description: str


class EventCreate(EventBase):
    pass


class Event(EventBase):
    id: int
    # Domyślnie pusta lista, jeśli nie ma zdjęć
    images: List[Image] = []
    model_config = ConfigDict(from_attributes=True)


# --- SCHEMATY DLA PROJEKTÓW ---


class ProjectBase(BaseModel):
    name: str
    description: str
    technologies: str
    year: Optional[int] = None


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int
    # Pełna struktura projektu wraz z powiązanymi obiektami
    images: List[Image] = []
    executable: List[ExecutableFile] = []
    files: List[ProjectFiles] = []
    model_config = ConfigDict(from_attributes=True)


# --- SCHEMATY DLA INFO ---


class GroupInfoBase(BaseModel):
    name: str
    description: str
    contact: str


class GroupInfoCreate(GroupInfoBase):
    pass


class GroupInfo(GroupInfoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
