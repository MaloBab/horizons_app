from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from typing import List

from ..database import get_db
from ..models.volunteer import Volunteer
from ..crud.volunteer import create_volunteer, delete_all_volunteers, get_volunteer, get_volunteers, delete_volunteer
from ..crud.volunteer_links import (
    add_slot_to_volunteer,
    remove_slot_from_volunteer,
    add_mate_to_volunteer,
    remove_mate_from_volunteer,
)
from ..crud.slot import get_or_create_slot
from .. import schemas

router = APIRouter(prefix="/volunteers", tags=["volunteers"])


# ─────────────────────────────────────────────────────────────────────────────
# CRUD de base
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[schemas.VolunteerResponse])
def list_volunteers(skip: int = 0, db: Session = Depends(get_db)):
    return get_volunteers(db, skip=skip)


@router.post("/", response_model=schemas.VolunteerResponse, status_code=201)
def create_volunteer_route(payload: schemas.VolunteerCreate, db: Session = Depends(get_db)):
    """Crée un bénévole manuellement (hors import Excel)."""
    return create_volunteer(db, payload)


@router.get("/{volunteer_id}", response_model=schemas.VolunteerResponse)
def get_volunteer_route(volunteer_id: UUID, db: Session = Depends(get_db)):
    volunteer = get_volunteer(db, volunteer_id)
    if not volunteer:
        raise HTTPException(status_code=404, detail="Bénévole introuvable")
    return volunteer


@router.delete("/{volunteer_id}", status_code=204)
def delete_volunteer_route(volunteer_id: UUID, db: Session = Depends(get_db)):
    if not delete_volunteer(db, volunteer_id):
        raise HTTPException(status_code=404, detail="Bénévole introuvable")


@router.delete("/", status_code=204)
def delete_all_volunteers_route(db: Session = Depends(get_db)):
    delete_all_volunteers(db)


# ─────────────────────────────────────────────────────────────────────────────
# Email
# ─────────────────────────────────────────────────────────────────────────────

class EmailUpdate(BaseModel):
    email: EmailStr


@router.patch("/{volunteer_id}/email", response_model=schemas.VolunteerResponse)
def update_email(volunteer_id: UUID, body: EmailUpdate, db: Session = Depends(get_db)):
    volunteer = get_volunteer(db, volunteer_id)
    if not volunteer:
        raise HTTPException(status_code=404, detail="Bénévole introuvable")

    conflict = db.query(Volunteer)\
        .filter(Volunteer.email == str(body.email))\
        .filter(Volunteer.id != volunteer_id)\
        .first()
    if conflict:
        raise HTTPException(status_code=409, detail="Cet email est déjà utilisé")

    setattr(volunteer, "email", str(body.email))
    db.commit()
    db.refresh(volunteer)
    return volunteer


# ─────────────────────────────────────────────────────────────────────────────
# Téléphone
# ─────────────────────────────────────────────────────────────────────────────

class PhoneUpdate(BaseModel):
    phone_number: str

@router.patch("/{volunteer_id}/phone", response_model=schemas.VolunteerResponse)
def update_phone(volunteer_id: UUID, body: PhoneUpdate, db: Session = Depends(get_db)):
    volunteer = get_volunteer(db, volunteer_id)
    if not volunteer:
        raise HTTPException(status_code=404, detail="Bénévole introuvable")

    setattr(volunteer, "phone_number", body.phone_number)
    db.commit()
    db.refresh(volunteer)
    return volunteer


# ─────────────────────────────────────────────────────────────────────────────
# Disponibilités — ajout par plage horaire, découpée en créneaux d'1h
# ─────────────────────────────────────────────────────────────────────────────

class AvailabilityRange(BaseModel):
    day_index:  int
    start_time: int   # heure de début incluse  (ex: 8)
    end_time:   int   # heure de fin exclue     (ex: 10) → crée 8h-9h et 9h-10h


@router.post("/{volunteer_id}/slots", response_model=schemas.VolunteerResponse)
def add_availability(volunteer_id: UUID, body: AvailabilityRange, db: Session = Depends(get_db)):
    volunteer = get_volunteer(db, volunteer_id)
    if not volunteer:
        raise HTTPException(status_code=404, detail="Bénévole introuvable")

    if body.start_time >= body.end_time:
        raise HTTPException(status_code=422, detail="start_time doit être strictement inférieur à end_time")

    existing_slot_ids = {vs.slot_id for vs in volunteer.slots}

    for hour in range(body.start_time, body.end_time):
        slot = get_or_create_slot(db, schemas.SlotCreate(
            day_index=body.day_index,
            start_time=hour,
            end_time=hour + 1,
        ))
        if slot.id not in existing_slot_ids:
            add_slot_to_volunteer(db, volunteer_id, slot.id)
            existing_slot_ids.add(slot.id)

    db.refresh(volunteer)
    return volunteer


@router.delete("/{volunteer_id}/slots/{slot_id}", response_model=schemas.VolunteerResponse)
def remove_slot(volunteer_id: UUID, slot_id: int, db: Session = Depends(get_db)):
    volunteer = get_volunteer(db, volunteer_id)
    if not volunteer:
        raise HTTPException(status_code=404, detail="Bénévole introuvable")

    remove_slot_from_volunteer(db, volunteer_id, slot_id)
    db.refresh(volunteer)
    return volunteer


# ─────────────────────────────────────────────────────────────────────────────
# Affinités (mates)
# ─────────────────────────────────────────────────────────────────────────────

class MateBody(BaseModel):
    mate_id: UUID


@router.post("/{volunteer_id}/mates", response_model=schemas.VolunteerResponse)
def add_mate(volunteer_id: UUID, body: MateBody, db: Session = Depends(get_db)):
    if volunteer_id == body.mate_id:
        raise HTTPException(status_code=422, detail="Un bénévole ne peut pas être son propre ami")

    volunteer = get_volunteer(db, volunteer_id)
    if not volunteer:
        raise HTTPException(status_code=404, detail="Bénévole introuvable")

    if not get_volunteer(db, body.mate_id):
        raise HTTPException(status_code=404, detail="Bénévole (ami) introuvable")

    if any(f.id == body.mate_id for f in volunteer.mates):
        raise HTTPException(status_code=409, detail="Ce lien d'affinité existe déjà")

    try:
        add_mate_to_volunteer(db, volunteer_id, body.mate_id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ce lien d'affinité existe déjà")

    db.refresh(volunteer)
    return volunteer


class PreferenceRankUpdate(BaseModel):
    preference_id: int
    rank: int = Field(..., ge=1)


@router.patch("/{volunteer_id}/preferences", response_model=schemas.VolunteerResponse)
def reorder_preferences(
    volunteer_id: UUID,
    body: List[PreferenceRankUpdate],
    db: Session = Depends(get_db),
):
    volunteer = get_volunteer(db, volunteer_id)
    if not volunteer:
        raise HTTPException(status_code=404, detail="Bénévole introuvable")

    existing_ids = {vp.preference_id for vp in volunteer.preferences}
    for item in body:
        if item.preference_id not in existing_ids:
            raise HTTPException(
                status_code=422,
                detail=f"La préférence {item.preference_id} n'appartient pas à ce bénévole"
            )

    pref_map = {vp.preference_id: vp for vp in volunteer.preferences}

    # ── Étape 1 : rangs temporaires négatifs pour éviter les collisions ──────
    for vp in volunteer.preferences:
        vp.rank = -vp.rank
    db.flush()

    # ── Étape 2 : rangs définitifs ────────────────────────────────────────────
    for item in body:
        pref_map[item.preference_id].rank = item.rank
    db.flush()

    db.commit()
    db.refresh(volunteer)
    return volunteer


@router.delete("/{volunteer_id}/mates/{mate_id}", response_model=schemas.VolunteerResponse)
def remove_mate(volunteer_id: UUID, mate_id: UUID, db: Session = Depends(get_db)):
    volunteer = get_volunteer(db, volunteer_id)
    if not volunteer:
        raise HTTPException(status_code=404, detail="Bénévole introuvable")

    remove_mate_from_volunteer(db, volunteer_id, mate_id)
    db.refresh(volunteer)
    return volunteer