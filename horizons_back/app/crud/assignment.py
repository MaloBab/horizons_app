from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from typing import List

from .. import models


# ─────────────────────────────────────────────────────────────────────────────
# Lecture
# ─────────────────────────────────────────────────────────────────────────────

def get_assignments(db: Session) -> List[models.Assignment]:
    """Retourne toutes les affectations avec leurs relations eager-loadées."""
    return (
        db.query(models.Assignment)
        .options(
            joinedload(models.Assignment.volunteer),
            joinedload(models.Assignment.job)
            .joinedload(models.job.Job.category),
            joinedload(models.Assignment.job)
            .joinedload(models.job.Job.slot),
        )
        .all()
    )


def get_assignment(
    db: Session, volunteer_id: UUID, job_id: int
) -> models.Assignment | None:
    return (
        db.query(models.Assignment)
        .filter_by(volunteer_id=volunteer_id, job_id=job_id)
        .first()
    )


# ─────────────────────────────────────────────────────────────────────────────
# Création / Suppression unitaire
# ─────────────────────────────────────────────────────────────────────────────

def create_assignment(
    db: Session, volunteer_id: UUID, job_id: int
) -> models.Assignment | None:
    """
    Crée une affectation. Retourne None si elle existe déjà (idempotent).
    Lève ValueError si le volunteer ou le job est introuvable.
    """
    volunteer = db.query(models.volunteer.Volunteer).filter_by(id=volunteer_id).first()
    if not volunteer:
        raise ValueError(f"Bénévole {volunteer_id} introuvable")

    job = db.query(models.job.Job).filter_by(id=job_id).first()
    if not job:
        raise ValueError(f"Poste {job_id} introuvable")

    existing = get_assignment(db, volunteer_id, job_id)
    if existing:
        return existing

    db_assignment = models.Assignment(
        volunteer_id=volunteer_id,
        job_id=job_id,
    )
    db.add(db_assignment)
    try:
        db.commit()
        db.refresh(db_assignment)
    except IntegrityError:
        db.rollback()
        return get_assignment(db, volunteer_id, job_id)

    return db_assignment


def delete_assignment(db: Session, volunteer_id: UUID, job_id: int) -> bool:
    """Supprime une affectation. Retourne False si elle n'existait pas."""
    assignment = get_assignment(db, volunteer_id, job_id)
    if not assignment:
        return False
    db.delete(assignment)
    db.commit()
    return True

    

# ─────────────────────────────────────────────────────────────────────────────
# Replace-all (bulk save)
# ─────────────────────────────────────────────────────────────────────────────

def replace_all_assignments(
    db: Session,
    pairs: List[tuple[UUID, int]],
) -> List[models.Assignment]:
    """
    Remplace l'intégralité des affectations en base par la liste fournie.
    Stratégie replace-all : DELETE tous + INSERT nouveaux dans une transaction.
    Retourne la liste des affectations persistées avec leurs relations.
    """
    # Suppression en masse sans charger les objets en mémoire
    db.query(models.Assignment).delete(synchronize_session=False)
    db.flush()

    new_assignments = []
    seen: set[tuple[str, int]] = set()

    for volunteer_id, job_id in pairs:
        key = (str(volunteer_id), job_id)
        if key in seen:
            continue
        seen.add(key)
        db_assignment = models.Assignment(
            volunteer_id=volunteer_id,
            job_id=job_id,
        )
        db.add(db_assignment)
        new_assignments.append(db_assignment)

    db.commit()

    # Rechargement avec relations pour la réponse
    return get_assignments(db)