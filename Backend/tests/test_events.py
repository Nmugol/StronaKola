from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import models


def test_create_event(client: TestClient, db: Session):
    response = client.post(
        "/api/admin/events/",
        json={
            "name": "Test Event",
            "description": "Test Description",
            "date": datetime.now().isoformat(),
        },
        headers={"X-API-Key": "test_api_key"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Event"
    assert data["description"] == "Test Description"
    assert "id" in data
    event_id = data["id"]

    event_in_db = db.query(models.Event).filter(models.Event.id == event_id).first()
    assert event_in_db is not None
    assert event_in_db.name == "Test Event"


def test_read_events(client: TestClient):
    response = client.get("/api/events/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_read_event(client: TestClient, db: Session):
    event = models.Event(
        name="Test Event 2", description="Test Description 2", date=datetime.now()
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    response = client.get(f"/api/events/{event.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Event 2"
    assert data["id"] == event.id


def test_read_inexistent_event(client: TestClient):
    response = client.get("/api/events/999")
    assert response.status_code == 404


def test_update_event(client: TestClient, db: Session):
    event = models.Event(
        name="Test Event 3", description="Test Description 3", date=datetime.now()
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    response = client.put(
        f"/api/admin/events/{event.id}",
        json={
            "name": "Updated Event",
            "description": "Updated Description",  # Dodaj brakujące pola
            "date": datetime.now().isoformat(),  # Dodaj brakujące pola
        },
        headers={"X-API-Key": "test_api_key"},
    )
    assert response.status_code == 200  # Teraz powinno przejść
    data = response.json()
    assert data["name"] == "Updated Event"

    db.refresh(event)
    assert event.name == "Updated Event"


def test_delete_event(client: TestClient, db: Session):
    event = models.Event(
        name="Test Event 4", description="Test Description 4", date=datetime.now()
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    response = client.delete(
        f"/api/admin/events/{event.id}", headers={"X-API-Key": "test_api_key"}
    )
    assert response.status_code == 200

    event_in_db = db.query(models.Event).filter(models.Event.id == event.id).first()
    assert event_in_db is None
