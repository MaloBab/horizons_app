from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..database import get_db
from ..crud import category as crud
from ..schemas.category import (
    CategoryCreate, CategoryResponse, CategoryUpdate
)

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return crud.get_categories(db)

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    cat = crud.get_category(db, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Catégorie introuvable")
    return cat

@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    cat = crud.create_category(db, category)
    db.commit()
    return cat

@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)):
    cat = crud.update_category(db, category_id, payload)
    if not cat:
        raise HTTPException(status_code=404, detail="Catégorie introuvable")
    db.commit()
    return cat

@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    try:
        if not crud.delete_category(db, category_id):
            raise HTTPException(status_code=404, detail="Catégorie introuvable")
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ce pôle est utilisé par des postes existants et ne peut pas être supprimé."
        )