from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..dependencies import get_db, verify_api_key
from ..models import models, schemas

router = APIRouter()


@router.get("/about/", response_model=schemas.GroupInfo)
def read_group_info(db: Session = Depends(get_db)):
    """PUBLICZNY: Informacje o grupie."""
    group_info = db.query(models.GroupInfo).first()
    if group_info is None:
        raise HTTPException(status_code=404, detail="Group info not found")
    return group_info


@router.post(
    "/admin/about/",
    response_model=schemas.GroupInfo,
    dependencies=[Depends(verify_api_key)],
)
def create_group_info(
    group_info: schemas.GroupInfoCreate, db: Session = Depends(get_db)
):
    """ADMIN: Tworzenie info (tylko raz)."""
    db_group_info = db.query(models.GroupInfo).first()
    if db_group_info:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Group info already exists, please update it.",
        )

    db_group_info = models.GroupInfo(**group_info.model_dump())
    db.add(db_group_info)
    db.commit()
    db.refresh(db_group_info)
    return db_group_info


@router.put(
    "/admin/about/",
    response_model=schemas.GroupInfo,
    dependencies=[Depends(verify_api_key)],
)
def update_group_info(
    group_info: schemas.GroupInfoCreate, db: Session = Depends(get_db)
):
    """ADMIN: Aktualizacja info."""
    db_group_info = db.query(models.GroupInfo).first()
    if db_group_info is None:
        raise HTTPException(
            status_code=404, detail="Group info not found, please create it first."
        )

    update_data = group_info.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_group_info, key, value)

    db.commit()
    db.refresh(db_group_info)
    return db_group_info
