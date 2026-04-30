# app/routes/assignments.py
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app import models

from ..database import get_db
from .. import schemas
from ..crud.assignment import (
    get_assignments,
    get_assignment,
    create_assignment,
    delete_assignment,
    replace_all_assignments,
)

from ..services.pipeline_service import run_pipeline
from ..services.task_manager import create_task, update_task, get_task

router = APIRouter(prefix="/assignments", tags=["assignments"])


# ─────────────────────────────────────────────────────────────────────────────
# Lecture
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[schemas.AssignmentResponse])
def list_assignments(db: Session = Depends(get_db)):
    """Retourne toutes les affectations courantes avec leurs relations."""
    return get_assignments(db)


# ─────────────────────────────────────────────────────────────────────────────
# Création / Suppression unitaire
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/", response_model=schemas.AssignmentResponse, status_code=201)
def create_assignment_route(
    body: schemas.AssignmentCreate,
    db:   Session = Depends(get_db),
):
    """Crée une affectation unique. Idempotent si elle existe déjà (retourne 200)."""
    try:
        assignment = create_assignment(db, body.volunteer_id, body.job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if assignment is None:
        raise HTTPException(status_code=409, detail="Affectation déjà existante")

    return assignment


@router.delete("/", status_code=204)
def delete_all_assignments(db: Session = Depends(get_db)):
    """Supprime toutes les affectations en base."""
    db.query(models.Assignment).delete(synchronize_session=False)
    db.commit()


@router.delete("/{volunteer_id}/{job_id}", status_code=204)
def delete_assignment_route(
    volunteer_id: UUID,
    job_id:       int,
    db:           Session = Depends(get_db),
):
    """Supprime une affectation unitaire."""
    if not delete_assignment(db, volunteer_id, job_id):
        raise HTTPException(status_code=404, detail="Affectation introuvable")


# ─────────────────────────────────────────────────────────────────────────────
# Bulk save (replace-all)
# ─────────────────────────────────────────────────────────────────────────────

@router.put("/bulk", response_model=List[schemas.AssignmentResponse])
def bulk_replace_assignments(
    body: schemas.BulkAssignmentPayload,
    db:   Session = Depends(get_db),
):
    """
    Remplace l'intégralité des affectations en base par la liste fournie.
    Opération atomique — en cas d'erreur, rien n'est modifié.
    """
    pairs = [(a.volunteer_id, a.job_id) for a in body.assignments]
    try:
        return replace_all_assignments(db, pairs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la sauvegarde : {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Algorithme génétique — Architecture polling (remplace l'ancien SSE)
#
# AVANT : GET /run-algorithm  → connexion SSE maintenue 48 minutes → timeout Cloudflare
# APRÈS : POST /run-algorithm → répond immédiatement avec un task_id (< 50 ms)
#         GET  /run-algorithm/{task_id} → interrogé toutes les 4s par le frontend
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/run-algorithm", status_code=202)
def launch_algorithm(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Lance l'algorithme génétique en tâche de fond.
    Répond immédiatement avec un task_id.
    Le frontend doit ensuite interroger GET /run-algorithm/{task_id} toutes les 4 secondes.
    """
    task_id = create_task()
    background_tasks.add_task(_run_algorithm_task, task_id, db)
    return {"task_id": task_id}


def _run_algorithm_task(task_id: str, db: Session):
    """
    Tâche de fond : exécute run_pipeline et écrit la progression dans task_manager.
    Tourne dans le thread pool de FastAPI — totalement découplé du cycle HTTP.
    """
    update_task(task_id, status="running", pct=0, msg="Initialisation…")

    def on_progress(pct: int, msg: str, extra: dict = {}):
        payload: dict = {"status": "running", "pct": pct, "msg": msg}
        # Filtre les valeurs None et Ellipsis avant de stocker
        payload.update({
            k: v for k, v in extra.items()
            if v is not None and not isinstance(v, type(...))
        })
        update_task(task_id, **payload)

    try:
        assignments = run_pipeline(db, on_progress=on_progress)
        result = [
            {"volunteer_id": str(a.volunteer_id), "job_id": a.job_id}
            for a in assignments
        ]
        update_task(
            task_id,
            status="done",
            pct=100,
            msg=f"{len(result)} affectations générées",
            assignments=result,
        )
    except Exception as e:
        update_task(task_id, status="error", error=str(e))


@router.get("/run-algorithm/{task_id}")
def get_algorithm_progress(task_id: str):
    """
    Endpoint de polling — interrogé toutes les 4 secondes par le frontend.
    Retourne l'état courant de la tâche (pct, msg, status, assignments, error).
    Chaque requête dure < 10 ms ; aucun timeout Cloudflare ne peut se déclencher.
    """
    task = get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Tâche introuvable ou expirée")
    return task