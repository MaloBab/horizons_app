from sqlalchemy.orm import Session
from .. import models, schemas

def get_job(db: Session, job_id: int):
    return db.query(models.Job).filter(models.Job.id == job_id).first()

def get_jobs(db: Session, skip: int = 0):
    return db.query(models.Job).offset(skip).all()

def create_job(db: Session, job: schemas.JobCreate, category_id: int, slot_id: int):
    db_job = models.Job(
        name=job.name,
        required_volunteers=job.required_volunteers,
        recruitment_type=job.recruitment_type,
        responsible=job.responsible,
        sort_order=job.sort_order,
        category_id=category_id,
        slot_id=slot_id,
    )
    db.add(db_job)
    db.flush()       # rend db_job.id disponible sans committer
    db.refresh(db_job)
    return db_job

def update_job(db: Session, job_id: int, job_update: schemas.JobUpdate):
    db_job = get_job(db, job_id)
    if db_job:
        for key, value in job_update.model_dump(exclude_unset=True).items():
            setattr(db_job, key, value)
        db.flush()
        db.refresh(db_job)
    return db_job

def delete_job(db: Session, job_id: int):
    db_job = get_job(db, job_id)
    if db_job:
        db.delete(db_job)
        db.flush()
        return True
    return False