from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from ..models import models, schemas
from ..dependencies import get_db, verify_api_key
import os
import shutil

router = APIRouter()

# Directory to store uploaded images
UPLOAD_DIR = "static/images"

@router.post("/admin/upload_image/", response_model=schemas.Image, dependencies=[Depends(verify_api_key)])
async def upload_image(
    file: UploadFile = File(...),
    event_id: Optional[int] = Form(None),
    project_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    file_extension = file.filename.split(".")[-1]
    if file_extension.lower() not in ["jpg", "jpeg", "png", "gif"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPG, JPEG, PNG, GIF are allowed.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if event_id:
        db_entity = db.query(models.Event).filter(models.Event.id == event_id).first()
        if not db_entity:
            raise HTTPException(status_code=404, detail="Event not found")
        db_image = models.Image(file_path=file_path, event_id=event_id)
    elif project_id:
        db_entity = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not db_entity:
            raise HTTPException(status_code=404, detail="Project not found")
        db_image = models.Image(file_path=file_path, project_id=project_id)
    else:
        raise HTTPException(status_code=400, detail="Either event_id or project_id must be provided")

    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

@router.get("/gallery/event/{event_id}", response_model=List[schemas.Image])
def get_event_images(event_id: int, db: Session = Depends(get_db)):
    images = db.query(models.Image).filter(models.Image.event_id == event_id).all()
    return images

@router.get("/gallery/project/{project_id}", response_model=List[schemas.Image])
def get_project_images(project_id: int, db: Session = Depends(get_db)):
    images = db.query(models.Image).filter(models.Image.project_id == project_id).all()
    return images

@router.delete("/admin/images/{image_id}", dependencies=[Depends(verify_api_key)])
def delete_image(image_id: int, db: Session = Depends(get_db)):
    db_image = db.query(models.Image).filter(models.Image.id == image_id).first()
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    
    if os.path.exists(db_image.file_path):
        os.remove(db_image.file_path)
    
    db.delete(db_image)
    db.commit()
    return {"message": "Image deleted successfully"}
