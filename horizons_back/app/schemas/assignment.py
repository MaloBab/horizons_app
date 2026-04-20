from pydantic import BaseModel, ConfigDict
from uuid import UUID
from .job import JobResponse
from .volunteer import VolunteerShortResponse


# ─────────────────────────────────────────────────────────────────────────────
# Payloads entrants
# ─────────────────────────────────────────────────────────────────────────────

class AssignmentCreate(BaseModel):
    volunteer_id: UUID
    job_id:       int


class BulkAssignmentPayload(BaseModel):
    """Payload pour le replace-all — liste complète des affectations souhaitées."""
    assignments: list[AssignmentCreate]


# ─────────────────────────────────────────────────────────────────────────────
# Réponses
# ─────────────────────────────────────────────────────────────────────────────

class AssignmentResponse(BaseModel):
    """
    Représentation d'une affectation retournée par l'API.
    Clé primaire composite (volunteer_id, job_id) — pas de champ id.
    """
    volunteer_id: UUID
    job_id:       int
    volunteer:    VolunteerShortResponse
    job:          JobResponse

    model_config = ConfigDict(from_attributes=True)