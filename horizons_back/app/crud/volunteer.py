from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from .. import models, schemas
import random

def create_volunteer(db: Session, volunteer: schemas.VolunteerCreate):
    db_volunteer = models.volunteer.Volunteer(
        first_name=volunteer.first_name,
        last_name=volunteer.last_name,
        email=volunteer.email,
        address=volunteer.address,
        phone_number=volunteer.phone_number,
        volunteer_type=volunteer.volunteer_type,
    )

    db.add(db_volunteer)
    db.flush()

    seen: set[int] = set()
    for index, pref_id in enumerate(volunteer.preference_ids):
        if pref_id in seen:
            continue
        seen.add(pref_id)
        db.add(models.volunteer.VolunteerPreference(
            volunteer_id=db_volunteer.id,
            preference_id=pref_id,
            rank=index + 1
        ))

    if volunteer.slot_ids:
        for s_id in volunteer.slot_ids:
            db.add(models.volunteer.VolunteerSlot(
                volunteer_id=db_volunteer.id,
                slot_id=s_id
            ))

    db.commit()
    db.refresh(db_volunteer)
    return db_volunteer

def get_volunteer(db: Session, volunteer_id: UUID):
    return db.query(models.volunteer.Volunteer).filter(models.volunteer.Volunteer.id == volunteer_id).first()

def get_volunteers(db: Session, skip: int = 0):
    return db.query(models.volunteer.Volunteer).offset(skip).all()


def delete_volunteer(db: Session, volunteer_id: UUID):
    
    volunteer = db.query(models.volunteer.Volunteer).filter(models.volunteer.Volunteer.id == volunteer_id).first()
    if volunteer:
        db.query(models.assignment.Assignment).filter(models.assignment.Assignment.volunteer_id == volunteer_id).delete(synchronize_session=False)
        db.query(models.volunteer.VolunteerPreference).filter(models.volunteer.VolunteerPreference.volunteer_id == volunteer_id).delete(synchronize_session=False)
        db.query(models.volunteer.VolunteerSlot).filter(models.volunteer.VolunteerSlot.volunteer_id == volunteer_id).delete(synchronize_session=False)
        db.query(models.volunteer.VolunteerMate).filter(models.volunteer.VolunteerMate.volunteer_id == volunteer_id).delete(synchronize_session=False)

        db.delete(volunteer)
        db.commit()
        return True
    return False


def _delete_all_volunteers_flush(db: Session) -> None:
    """Supprime tous les bénévoles sans commit.
    À utiliser à l'intérieur d'une transaction gérée par l'appelant
    (ex: import_volunteer_service) pour garantir l'atomicité.
    """
    db.query(models.assignment.Assignment).delete(synchronize_session=False)
    db.query(models.volunteer.VolunteerPreference).delete(synchronize_session=False)
    db.query(models.volunteer.VolunteerSlot).delete(synchronize_session=False)
    db.query(models.volunteer.VolunteerMate).delete(synchronize_session=False)
    db.query(models.volunteer.Volunteer).delete(synchronize_session=False)
 
def delete_all_volunteers(db: Session) -> None:
    """Supprime tous les bénévoles et leurs données liées, puis commit.
    À utiliser depuis les routes — pas depuis un service transactionnel.
    """
    _delete_all_volunteers_flush(db)
    db.commit()
 
def resolve_mates(db: Session, volunteer_email: str, mate_emails: List[str]) -> None:
    volunteer = db.query(models.volunteer.Volunteer).filter_by(email=volunteer_email).first()
    if not volunteer:
        return
    for mate_email in mate_emails:
        mate = db.query(models.volunteer.Volunteer).filter_by(email=mate_email).first()
        if not mate:
            continue
        already_exists = db.query(models.volunteer.VolunteerMate).filter_by(
            volunteer_id=volunteer.id, mate_id=mate.id
        ).first()
        if not already_exists:
            db.add(models.volunteer.VolunteerMate(volunteer_id=volunteer.id, mate_id=mate.id))
    db.commit()
    