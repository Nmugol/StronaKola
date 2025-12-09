import os
import shutil
from this import s
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..dependencies import get_db, verify_api_key
from ..models import models, schemas

router = APIRouter()

# Katalog dla zdjęć
IMG_DIR = "static/images"

# Upewnij się, że katalog istnieje
os.makedirs(IMG_DIR, exist_ok=True)


def save_file(file: UploadFile, destination_dir: str) -> str:
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    file_path = os.path.join(destination_dir, str(file.filename))
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_path


# --- OBRAZY (IMAGES) - DOSTĘP TYLKO DLA ADMINA (UPLOAD/DELETE) ---


@router.post(
    "/admin/upload_image/",
    response_model=schemas.Image,
    dependencies=[Depends(verify_api_key)],
)
async def upload_image(
    file: UploadFile = File(...),
    event_id: Optional[int] = Form(None),
    project_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
):
    file_name = file.filename or "image"
    file_extension = file_name.split(".")[-1]
    if file_extension.lower() not in ["jpg", "jpeg", "png", "gif", "webp"]:
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only images allowed."
        )

    file_path = save_file(file, IMG_DIR)

    db_image = None
    if event_id:
        if not db.query(models.Event).filter(models.Event.id == event_id).first():
            raise HTTPException(status_code=404, detail="Event not found")
        db_image = models.Image(file_path=file_path, event_id=event_id)
    elif project_id:
        if not db.query(models.Project).filter(models.Project.id == project_id).first():
            raise HTTPException(status_code=404, detail="Project not found")
        db_image = models.Image(file_path=file_path, project_id=project_id)
    else:
        raise HTTPException(
            status_code=400, detail="Either event_id or project_id must be provided"
        )

    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


@router.delete("/admin/images/{image_id}", dependencies=[Depends(verify_api_key)])
def delete_image(image_id: int, db: Session = Depends(get_db)):
    """
    Admin: Usuwa zdjęcie.
    """
    db_image = db.query(models.Image).filter(models.Image.id == image_id).first()
    if not db_image:
        raise HTTPException(status_code=404, detail="Image not found")

    if os.path.exists(str(db_image.file_path)):
        os.remove(str(db_image.file_path))

    db.delete(db_image)
    db.commit()
    return {"message": "Image deleted successfully"}
