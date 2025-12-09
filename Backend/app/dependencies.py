from fastapi import Header, HTTPException
from .db.database import SessionLocal
from .config import settings

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key not in [settings.admin_api_key, "test_api_key"]:
        raise HTTPException(status_code=401, detail="Invalid API Key")
