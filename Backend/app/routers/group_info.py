from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..models import models, schemas
from ..dependencies import get_db, verify_api_key

router = APIRouter()

@router.post("/admin/about/", response_model=schemas.GroupInfo, dependencies=[Depends(verify_api_key)])
def create_group_info(group_info: schemas.GroupInfoCreate, db: Session = Depends(get_db)):
    db_group_info = db.query(models.GroupInfo).first()
    if db_group_info:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Group info already exists, please update it.")
    db_group_info = models.GroupInfo(**group_info.dict())
    db.add(db_group_info)
    db.commit()
    db.refresh(db_group_info)
    return db_group_info

@router.get("/about/", response_model=schemas.GroupInfo)
def read_group_info(db: Session = Depends(get_db)):
    group_info = db.query(models.GroupInfo).first()
    if group_info is None:
        raise HTTPException(status_code=404, detail="Group info not found")
    return group_info

@router.put("/admin/about/", response_model=schemas.GroupInfo, dependencies=[Depends(verify_api_key)])
def update_group_info(group_info: schemas.GroupInfoCreate, db: Session = Depends(get_db)):
    db_group_info = db.query(models.GroupInfo).first()
    if db_group_info is None:
        raise HTTPException(status_code=404, detail="Group info not found, please create it first.")
    for key, value in group_info.dict().items():
        setattr(db_group_info, key, value)
    db.commit()
    db.refresh(db_group_info)
    return db_group_info

