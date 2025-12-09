import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import models

# --- POPRAWKA: Dostosowanie pól do models.py i schemas.py ---
GROUP_INFO_DATA = {
    "name": "Nasze Koło Naukowe",
    "description": "Jesteśmy super grupą pasjonatów.",
    "contact": "kontakt@kolo.pl",  # Zmieniono z 'contact_email' na 'contact'
    # Usunięto 'facebook_link', ponieważ nie ma go w Twoim modelu GroupInfo
}


def test_read_group_info_empty(client: TestClient, db: Session):
    """
    Testuje sytuację, gdy w bazie nie ma jeszcze informacji (404).
    """
    response = client.get("/api/about/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Group info not found"


def test_create_group_info(client: TestClient, db: Session):
    """
    Testuje poprawne utworzenie informacji przez admina.
    """
    response = client.post(
        "/api/admin/about/", json=GROUP_INFO_DATA, headers={"X-API-Key": "test_api_key"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == GROUP_INFO_DATA["name"]
    assert data["description"] == GROUP_INFO_DATA["description"]
    assert data["contact"] == GROUP_INFO_DATA["contact"]

    # Weryfikacja w bazie
    db_info = db.query(models.GroupInfo).first()
    assert db_info is not None
    assert db_info.name == "Nasze Koło Naukowe"


def test_create_group_info_duplicate(client: TestClient, db: Session):
    """
    Testuje blokadę przed utworzeniem drugiego wpisu (409 Conflict).
    """
    # 1. Tworzymy pierwszy wpis
    info = models.GroupInfo(**GROUP_INFO_DATA)
    db.add(info)
    db.commit()

    # 2. Próbujemy utworzyć drugi
    response = client.post(
        "/api/admin/about/",
        json={
            "name": "Inne Koło",
            "description": "Atak klonów",
            "contact": "inny@mail.pl",
        },
        headers={"X-API-Key": "test_api_key"},
    )

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]

    # Upewniamy się, że w bazie nadal jest tylko 1 wpis
    count = db.query(models.GroupInfo).count()
    assert count == 1


def test_read_group_info_existing(client: TestClient, db: Session):
    """
    Testuje pobieranie informacji, gdy już istnieją.
    """
    # Setup
    info = models.GroupInfo(**GROUP_INFO_DATA)
    db.add(info)
    db.commit()

    # Action
    response = client.get("/api/about/")

    # Assert
    assert response.status_code == 200
    data = response.json()
    # POPRAWKA: Sprawdzamy pole 'contact', a nie 'contact_email'
    assert data["contact"] == "kontakt@kolo.pl"


def test_update_group_info(client: TestClient, db: Session):
    """
    Testuje aktualizację istniejących danych.
    """
    # Setup
    info = models.GroupInfo(**GROUP_INFO_DATA)
    db.add(info)
    db.commit()

    # Action
    new_data = {
        "name": "Zaktualizowana Nazwa",
        "description": "Nowy opis",
        # POPRAWKA: Używamy poprawnej nazwy pola 'contact'
        "contact": "kontakt@kolo.pl",
    }

    response = client.put(
        "/api/admin/about/", json=new_data, headers={"X-API-Key": "test_api_key"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Zaktualizowana Nazwa"

    # Weryfikacja bazy
    db.refresh(info)
    assert info.name == "Zaktualizowana Nazwa"


def test_update_group_info_not_found(client: TestClient, db: Session):
    """
    Testuje próbę aktualizacji, gdy baza jest pusta (404).
    """
    response = client.put(
        "/api/admin/about/", json=GROUP_INFO_DATA, headers={"X-API-Key": "test_api_key"}
    )

    assert response.status_code == 404
    assert "create it first" in response.json()["detail"]
