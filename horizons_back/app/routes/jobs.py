from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from .. import models, schemas
from .. import crud
from ..database import get_db

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=List[schemas.JobResponse])
def list_jobs(skip: int = 0, db: Session = Depends(get_db)):
    return (
        db.query(models.Job)
        .options(joinedload(models.Job.category), joinedload(models.Job.slot))
        .offset(skip)
        .all()
    )


@router.get("/grouped", response_model=List[schemas.CategoryGroupResponse])
def list_jobs_grouped(db: Session = Depends(get_db)):
    categories = (
        db.query(models.Category)
        .options(
            joinedload(models.Category.jobs)
            .joinedload(models.Job.slot)
        )
        .order_by(models.Category.id)
        .all()
    )

    result = []
    for category in categories:
        # Groupement par (name, recruitment_type)
        groups: dict[tuple, list] = {}
        for job in sorted(category.jobs, key=lambda j: j.sort_order):
            key = (job.name, job.recruitment_type)
            groups.setdefault(key, []).append(job)

        job_groups = [
            schemas.JobGroupResponse(
                name=jobs[0].name,
                recruitment_type=jobs[0].recruitment_type,
                responsible=jobs[0].responsible,
                sort_order=jobs[0].sort_order,
                slots=jobs,
            )
            for (name, rtype), jobs in groups.items()
        ]

        result.append(schemas.CategoryGroupResponse(
            category=schemas.CategoryResponse.model_validate(category),
            jobs=job_groups,
        ))

    return result


@router.get("/{job_id}", response_model=schemas.JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = (
        db.query(models.Job)
        .options(joinedload(models.Job.category), joinedload(models.Job.slot))
        .filter(models.Job.id == job_id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Poste introuvable")
    return job


@router.post("/", response_model=schemas.JobResponse, status_code=201)
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    category = crud.category.get_or_create_category(db, job.category)
    slot = crud.slot.get_or_create_slot(db, job.slot)
    db_job = crud.job.create_job(db, job, category_id=category.id, slot_id=slot.id)
    db.commit()
    return (
        db.query(models.Job)
        .options(joinedload(models.Job.category), joinedload(models.Job.slot))
        .filter(models.Job.id == db_job.id)
        .first()
    )

@router.patch("/{job_id}", response_model=schemas.JobResponse)
def update_job(job_id: int, job_update: schemas.JobUpdate, db: Session = Depends(get_db)):
    db_job = crud.job.update_job(db, job_id, job_update)
    if not db_job:
        raise HTTPException(status_code=404, detail="Poste introuvable")
    db.commit()
    return (
        db.query(models.Job)
        .options(joinedload(models.Job.category), joinedload(models.Job.slot))
        .filter(models.Job.id == db_job.id)
        .first()
    )

@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    if not crud.job.delete_job(db, job_id):
        raise HTTPException(status_code=404, detail="Poste introuvable")
    db.commit()