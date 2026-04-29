from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
import asyncio
import json
import threading

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




@router.get("/run-algorithm")
async def run_algorithm_sse(db: Session = Depends(get_db)):
    """
    Lance l'algorithme génétique et streame la progression en SSE.
    Format : data: {"pct": 42, "msg": "Génération 42/100"}\n\n
    Dernier event : data: {"pct": 100, "done": true, "assignments": [...]}\n\n
    """
    queue: asyncio.Queue = asyncio.Queue()
    loop = asyncio.get_event_loop()

    def on_progress(pct: int, msg: str, extra: dict = {}):
        payload = {"pct": pct, "msg": msg}
        if extra:
            payload.update({
                k: v for k, v in extra.items()
                if v is not None and not isinstance(v, type(...))
            })
        loop.call_soon_threadsafe(queue.put_nowait, payload)

    def run_in_thread():
        try:
            assignments = run_pipeline(db, on_progress=on_progress)
            result = [{"volunteer_id": str(a.volunteer_id), "job_id": a.job_id} for a in assignments]
            loop.call_soon_threadsafe(queue.put_nowait, {"pct": 100, "done": True, "assignments": result})
        except Exception as e:
            loop.call_soon_threadsafe(queue.put_nowait, {"error": str(e)})

    thread = threading.Thread(target=run_in_thread, daemon=True)
    thread.start()

    async def event_stream():
        yield "data: {\"pct\": 0, \"msg\": \"Initialisation...\"}\n\n"
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=15.0)
                yield f"data: {json.dumps(event)}\n\n"
                
                if event.get("done") or event.get("error"):
                    break
            except asyncio.TimeoutError:
                yield ": keep-alive\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )