import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import models

# Importujemy moduł routera, aby podmienić ścieżki do folderów
from app.routers import projects as projects_router

# --------------------------------------------------------------------------
# POMOCNICY (HELPERS)
# --------------------------------------------------------------------------


def create_dummy_project(db: Session) -> models.Project:
    """Tworzy testowy projekt w bazie."""
    project = models.Project(
        name="Super Game",
        description="A great game",
        year=2024,
        technologies="Python, Raylib",  # <--- NAPRAWA: Dodano wymagane pole
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


# --------------------------------------------------------------------------
# TESTY: CRUD PROJEKTÓW
# --------------------------------------------------------------------------


def test_create_project(client: TestClient, db: Session):
    response = client.post(
        "/api/admin/projects/",
        json={
            "name": "New Project",
            "description": "Desc",
            "year": 2025,
            "technologies": "FastAPI, React",  # <--- NAPRAWA: Dodano wymagane pole
        },
        headers={"X-API-Key": "test_api_key"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Project"
    assert data["id"] is not None


def test_read_projects(client: TestClient, db: Session):
    create_dummy_project(db)
    response = client.get("/api/projects/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    # Możemy sprawdzić czy technologies są zwracane
    assert response.json()[0]["technologies"] == "Python, Raylib"


def test_update_project(client: TestClient, db: Session):
    project = create_dummy_project(db)
    response = client.put(
        f"/api/admin/projects/{project.id}",
        json={
            "name": "Updated Name",
            "year": 2030,
            "description": "Updated Desc",
            "technologies": "Updated Tech",  # <--- NAPRAWA: Dodano, jeśli schema tego wymaga
        },
        headers={"X-API-Key": "test_api_key"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"

    db.refresh(project)
    assert project.year == 2030


def test_delete_project(client: TestClient, db: Session):
    project = create_dummy_project(db)
    response = client.delete(
        f"/api/admin/projects/{project.id}", headers={"X-API-Key": "test_api_key"}
    )
    assert response.status_code == 200

    # Sprawdzenie czy zniknął
    response_get = client.get(f"/api/projects/{project.id}")
    assert response_get.status_code == 404


# --------------------------------------------------------------------------
# TESTY: PLIKI ŹRÓDŁOWE (ZIP)
# --------------------------------------------------------------------------


def test_upload_project_file_zip(client: TestClient, db: Session, tmp_path):
    # 1. SETUP: Podmieniamy katalog na tymczasowy
    projects_router.FILES_DIR = str(tmp_path)
    project = create_dummy_project(db)

    # 2. ACTION: Upload pliku ZIP
    file_content = b"PK...fake_zip_content"
    file_data = {"file": ("source.zip", file_content, "application/zip")}

    response = client.post(
        "/api/admin/projects/files/upload",
        files=file_data,
        data={"project_id": project.id},
        headers={"X-API-Key": "test_api_key"},
    )

    # 3. ASSERT
    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == project.id

    # Weryfikacja pliku na dysku
    saved_path = data["file_path"]
    assert os.path.exists(saved_path)


def test_upload_project_file_invalid_extension(
    client: TestClient, db: Session, tmp_path
):
    projects_router.FILES_DIR = str(tmp_path)
    project = create_dummy_project(db)

    file_data = {"file": ("virus.exe", b"content", "application/x-msdos-program")}

    response = client.post(
        "/api/admin/projects/files/upload",
        files=file_data,
        data={"project_id": project.id},
        headers={"X-API-Key": "test_api_key"},
    )
    assert response.status_code == 400
    assert "Only archive files allowed" in response.json()["detail"]


def test_delete_project_file(client: TestClient, db: Session, tmp_path):
    # Setup
    projects_router.FILES_DIR = str(tmp_path)
    project = create_dummy_project(db)

    # Ręczne utworzenie pliku i wpisu w bazie
    fake_file = tmp_path / "test.zip"
    fake_file.write_bytes(b"data")

    db_file = models.ProjectFiles(file_path=str(fake_file), project_id=project.id)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    # Action: Delete
    response = client.delete(
        f"/api/admin/projects/files/{db_file.id}", headers={"X-API-Key": "test_api_key"}
    )

    # Assert
    assert response.status_code == 200
    assert not fake_file.exists()  # Plik powinien zniknąć z dysku

    db.expire_all()
    assert db.query(models.ProjectFiles).filter_by(id=db_file.id).first() is None


# --------------------------------------------------------------------------
# TESTY: PLIKI WYKONYWALNE (EXE)
# --------------------------------------------------------------------------


def test_upload_executable(client: TestClient, db: Session, tmp_path):
    # 1. SETUP
    projects_router.EXE_DIR = str(tmp_path)
    project = create_dummy_project(db)

    # 2. ACTION
    file_data = {"file": ("game_setup.exe", b"exe_content", "application/octet-stream")}
    form_data = {
        "project_id": project.id,
        "version": "1.0.0",
        "platform": "WIN",  # <--- NAPRAWA: Używamy 'WIN' zamiast 'windows'
    }

    response = client.post(
        "/api/admin/projects/executables/upload",
        files=file_data,
        data=form_data,
        headers={"X-API-Key": "test_api_key"},
    )

    # 3. ASSERT
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "1.0.0"
    assert data["platform"] == "WIN"  # Oczekujemy 'WIN'
    assert os.path.exists(data["file_path"])


def test_upload_executable(client: TestClient, db: Session, tmp_path):
    # 1. SETUP
    projects_router.EXE_DIR = str(tmp_path)
    project = create_dummy_project(db)

    # 2. ACTION
    # Używamy .value, aby pobrać faktyczną wartość (np. "windows"), a nie nazwę klucza "WIN"
    platform_value = models.Platforms.WIN.value

    file_data = {"file": ("game_setup.exe", b"exe_content", "application/octet-stream")}
    form_data = {
        "project_id": project.id,
        "version": "1.0.0",
        "platform": platform_value,  # <--- POPRAWKA: Wysyłamy wartość z Enuma
    }

    response = client.post(
        "/api/admin/projects/executables/upload",
        files=file_data,
        data=form_data,
        headers={"X-API-Key": "test_api_key"},
    )

    # 3. ASSERT
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "1.0.0"
    assert data["platform"] == platform_value
    assert os.path.exists(data["file_path"])


def test_download_executable_public(client: TestClient, db: Session, tmp_path):
    # Setup
    projects_router.EXE_DIR = str(tmp_path)
    project = create_dummy_project(db)

    fake_exe = tmp_path / "game.exe"
    fake_exe.write_bytes(b"EXEDATA")

    # Używamy .value również tutaj dla spójności
    platform_value = models.Platforms.WIN.value

    db_exe = models.ExecutableFile(
        file_path=str(fake_exe),
        version="1.0",
        platform=platform_value,
        project_id=project.id,
    )
    db.add(db_exe)
    db.commit()

    # Action: Public Download
    # POPRAWKA: Dodano prefiks /api, żeby zgadzał się z konfiguracją routera
    response = client.get(f"/api/download/executable/{db_exe.id}")

    # Assert
    assert response.status_code == 200
    assert response.content == b"EXEDATA"
