import os
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import models
from app.routers import files as files_router  # Importujemy moduł, by podmienić katalog


# Helper: Tworzenie eventu, bo jest wymagany do przypisania zdjęcia
def create_dummy_event(db: Session):
    event = models.Event(
        name="Event for Image",
        description="Desc",
        date=datetime.now(),  # lub .isoformat() zależnie od modelu
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


# Helper: Tworzenie projektu
def create_dummy_project(db: Session):
    project = models.Project(name="Project for Image", description="Desc", year=2023)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def test_upload_image_to_event(client: TestClient, db: Session, tmp_path):
    """
    Testuje przesyłanie pliku. Używamy tmp_path, aby nie zapisywać
    na prawdziwym dysku w folderze static/.
    """
    # 1. SETUP: Podmieniamy katalog zapisu na tymczasowy folder testowy
    files_router.IMG_DIR = str(tmp_path)

    event = create_dummy_event(db)

    # 2. ACTION: Przygotowanie pliku i wysłanie
    # Format files w requests: {'nazwa_pola': ('nazwa_pliku', 'zawartość', 'mimetype')}
    file_data = {"file": ("test_image.jpg", b"fake_image_content", "image/jpeg")}

    # Dane formularza (event_id)
    form_data = {"event_id": event.id}

    response = client.post(
        "/api/admin/upload_image/",
        files=file_data,
        data=form_data,
        headers={"X-API-Key": "test_api_key"},
    )

    # 3. ASSERT
    assert response.status_code == 200
    data = response.json()

    # Sprawdź czy wpis w bazie istnieje
    assert data["event_id"] == event.id
    assert "file_path" in data

    # Sprawdź czy plik fizycznie powstał w folderze tymczasowym
    saved_path = data["file_path"]
    assert os.path.exists(saved_path)

    # Sprawdź czy zawartość pliku się zgadza
    with open(saved_path, "rb") as f:
        content = f.read()
        assert content == b"fake_image_content"


def test_upload_image_invalid_extension(client: TestClient, db: Session, tmp_path):
    """Testuje odrzucenie pliku z złym rozszerzeniem (np. .txt)."""
    files_router.IMG_DIR = str(tmp_path)

    file_data = {"file": ("malicious.txt", b"text_content", "text/plain")}
    form_data = {"event_id": 1}  # ID nie ma znaczenia, błąd powinien być wcześniej

    response = client.post(
        "/api/admin/upload_image/",
        files=file_data,
        data=form_data,
        headers={"X-API-Key": "test_api_key"},
    )

    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]


def test_upload_image_missing_parent(client: TestClient, db: Session, tmp_path):
    """Testuje próbę wysłania zdjęcia bez event_id ani project_id."""
    files_router.IMG_DIR = str(tmp_path)
    file_data = {"file": ("test.png", b"content", "image/png")}

    response = client.post(
        "/api/admin/upload_image/",
        files=file_data,
        data={},  # Pusty formularz
        headers={"X-API-Key": "test_api_key"},
    )

    assert response.status_code == 400
    assert "must be provided" in response.json()["detail"]


def test_delete_image(client: TestClient, db: Session, tmp_path):
    """Testuje usuwanie wpisu z bazy ORAZ pliku z dysku."""
    files_router.IMG_DIR = str(tmp_path)
    event = create_dummy_event(db)

    # 1. Ręczne stworzenie pliku i wpisu w bazie (symulacja stanu po uploadzie)
    # Tworzymy fizyczny plik
    fake_file_name = "image_to_delete.jpg"
    full_path = os.path.join(tmp_path, fake_file_name)
    with open(full_path, "wb") as f:
        f.write(b"data_to_delete")

    # Tworzymy wpis w bazie
    db_image = models.Image(file_path=full_path, event_id=event.id)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)

    # Upewnij się, że plik istnieje przed testem
    assert os.path.exists(full_path)

    # 2. ACTION: Usuwanie
    response = client.delete(
        f"/api/admin/images/{db_image.id}", headers={"X-API-Key": "test_api_key"}
    )

    # 3. ASSERT
    assert response.status_code == 200

    # Sprawdź czy wpis zniknął z bazy
    db.expire_all()
    deleted_img = db.query(models.Image).filter(models.Image.id == db_image.id).first()
    assert deleted_img is None

    # Sprawdź czy plik zniknął z dysku (Kluczowy test dla os.remove)
    assert not os.path.exists(full_path)
