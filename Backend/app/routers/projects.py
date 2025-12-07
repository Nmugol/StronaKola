import os
import shutil
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..dependencies import get_db, verify_api_key
from ..models import models, schemas

router = APIRouter()

# Konfiguracja katalogów
FILES_DIR = "static/project_files"
EXE_DIR = "static/executables"

os.makedirs(FILES_DIR, exist_ok=True)
os.makedirs(EXE_DIR, exist_ok=True)


def save_file(file: UploadFile, destination_dir: str) -> str:
    file_path = os.path.join(destination_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_path


# ==========================================
# SEKCJA 1: ZARZĄDZANIE PROJEKTAMI (CRUD)
# ==========================================


@router.get("/projects/", response_model=List[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """PUBLICZNY: Lista projektów (wraz ze zdjęciami i info o plikach)."""
    projects = db.query(models.Project).offset(skip).limit(limit).all()
    return projects


@router.get("/projects/{project_id}", response_model=schemas.Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    """PUBLICZNY: Szczegóły projektu."""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post(
    "/admin/projects/",
    response_model=schemas.Project,
    dependencies=[Depends(verify_api_key)],
)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    """ADMIN: Tworzenie projektu."""
    db_project = models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.put(
    "/admin/projects/{project_id}",
    response_model=schemas.Project,
    dependencies=[Depends(verify_api_key)],
)
def update_project(
    project_id: int, project: schemas.ProjectCreate, db: Session = Depends(get_db)
):
    """ADMIN: Edycja projektu."""
    db_project = (
        db.query(models.Project).filter(models.Project.id == project_id).first()
    )
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = project.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_project, key, value)

    db.commit()
    db.refresh(db_project)
    return db_project


@router.delete("/admin/projects/{project_id}", dependencies=[Depends(verify_api_key)])
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """ADMIN: Usuwanie projektu."""
    db_project = (
        db.query(models.Project).filter(models.Project.id == project_id).first()
    )
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # Uwaga: Pliki powiązane z projektem powinny zostać usunięte z dysku ręcznie
    # lub przez logikę w Pythonie, jeśli baza ma tylko ON DELETE CASCADE.
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted successfully"}


# ==========================================
# SEKCJA 2: PLIKI ŹRÓDŁOWE (ZIP) - TYLKO ADMIN
# ==========================================


@router.post(
    "/admin/projects/files/upload",
    response_model=schemas.ProjectFiles,
    dependencies=[Depends(verify_api_key)],
)
async def upload_project_file(
    file: UploadFile = File(...),
    project_id: int = Form(...),
    db: Session = Depends(get_db),
):
    """ADMIN: Upload kodów źródłowych (ZIP)."""
    if not db.query(models.Project).filter(models.Project.id == project_id).first():
        raise HTTPException(status_code=404, detail="Project not found")

    allowed_extensions = ["zip", "rar", "7z", "tar", "gz", "bz2"]
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Only archive files allowed.")

    file_path = save_file(file, FILES_DIR)
    db_file = models.ProjectFiles(file_path=file_path, project_id=project_id)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


@router.delete(
    "/admin/projects/files/{file_id}", dependencies=[Depends(verify_api_key)]
)
def delete_project_file(file_id: int, db: Session = Depends(get_db)):
    """ADMIN: Usuwanie kodów źródłowych."""
    db_file = (
        db.query(models.ProjectFiles).filter(models.ProjectFiles.id == file_id).first()
    )
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    if os.path.exists(db_file.file_path):
        os.remove(db_file.file_path)

    db.delete(db_file)
    db.commit()
    return {"message": "File deleted successfully"}


@router.get(
    "/admin/projects/files/{file_id}/download", dependencies=[Depends(verify_api_key)]
)
def download_project_file_admin(file_id: int, db: Session = Depends(get_db)):
    """
    ADMIN: Pobieranie kodów źródłowych.
    Brak publicznego odpowiednika (wymaga klucza API).
    """
    db_file = (
        db.query(models.ProjectFiles).filter(models.ProjectFiles.id == file_id).first()
    )
    if not db_file or not os.path.exists(db_file.file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=db_file.file_path,
        filename=os.path.basename(db_file.file_path),
        media_type="application/octet-stream",
    )


# ==========================================
# SEKCJA 3: PLIKI WYKONYWALNE (EXE) - ADMIN UPLOAD, PUBLIC DOWNLOAD
# ==========================================


@router.post(
    "/admin/projects/executables/upload",
    response_model=schemas.ExecutableFile,
    dependencies=[Depends(verify_api_key)],
)
async def upload_executable(
    file: UploadFile = File(...),
    project_id: int = Form(...),
    version: str = Form(...),
    platform: str = Form(...),
    db: Session = Depends(get_db),
):
    """ADMIN: Upload pliku .exe."""
    if not db.query(models.Project).filter(models.Project.id == project_id).first():
        raise HTTPException(status_code=404, detail="Project not found")

    allowed_platforms = [p.value for p in models.Platforms]
    if platform not in allowed_platforms:
        raise HTTPException(
            status_code=400, detail=f"Invalid platform. Choose: {allowed_platforms}"
        )

    file_path = save_file(file, EXE_DIR)
    db_exe = models.ExecutableFile(
        file_path=file_path, version=version, platform=platform, project_id=project_id
    )
    db.add(db_exe)
    db.commit()
    db.refresh(db_exe)
    return db_exe


@router.delete(
    "/admin/projects/executables/{exe_id}", dependencies=[Depends(verify_api_key)]
)
def delete_executable(exe_id: int, db: Session = Depends(get_db)):
    """ADMIN: Usuwanie pliku .exe."""
    db_exe = (
        db.query(models.ExecutableFile)
        .filter(models.ExecutableFile.id == exe_id)
        .first()
    )
    if not db_exe:
        raise HTTPException(status_code=404, detail="Executable not found")

    if os.path.exists(db_exe.file_path):
        os.remove(db_exe.file_path)

    db.delete(db_exe)
    db.commit()
    return {"message": "Executable deleted successfully"}


@router.get("/download/executable/{exe_id}")
def download_executable_public(exe_id: int, db: Session = Depends(get_db)):
    """
    PUBLICZNY: Pobieranie pliku .exe.
    Brak wymogu verify_api_key.
    """
    db_exe = (
        db.query(models.ExecutableFile)
        .filter(models.ExecutableFile.id == exe_id)
        .first()
    )
    if not db_exe:
        raise HTTPException(status_code=404, detail="Executable not found")

    if not os.path.exists(db_exe.file_path):
        raise HTTPException(status_code=404, detail="File missing on server")

    return FileResponse(
        path=db_exe.file_path,
        filename=os.path.basename(db_exe.file_path),
        media_type="application/octet-stream",
    )
