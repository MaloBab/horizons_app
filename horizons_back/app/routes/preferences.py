from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import preference as crud
from ..schemas.preference import (
    PreferenceCreate, PreferenceResponse, PreferenceUpdate
)

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("/", response_model=list[PreferenceResponse])
def list_preferences(db: Session = Depends(get_db)):
    return crud.get_preferences(db)

@router.get("/{preference_id}", response_model=PreferenceResponse)
def get_preference(preference_id: int, db: Session = Depends(get_db)):
    pref = crud.get_preference(db, preference_id)
    if not pref:
        raise HTTPException(status_code=404, detail="Préférence introuvable")
    return pref

@router.post("/", response_model=PreferenceResponse, status_code=201)
def create_preference(preference: PreferenceCreate, db: Session = Depends(get_db)):
    return crud.create_preference(db, preference)

@router.delete("/{preference_id}", status_code=204)
def delete_preference(preference_id: int, db: Session = Depends(get_db)):
    if not crud.delete_preference(db, preference_id):
        raise HTTPException(status_code=404, detail="Préférence introuvable")
    
@router.patch("/{preference_id}", response_model=PreferenceResponse)
def update_preference(preference_id: int, payload: PreferenceUpdate, db: Session = Depends(get_db)):
    pref = crud.rename_preference(db, preference_id, payload.label)
    if not pref:
        raise HTTPException(status_code=404, detail="Préférence introuvable")
    return pref