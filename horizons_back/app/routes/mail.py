"""
routes/mail.py

Endpoint d'envoi batch de mails personnalisés aux bénévoles.
POST /mail/send-batch
"""
from __future__ import annotations

import asyncio
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import traceback
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..core.security import get_current_user
from ..crud.festival import get_festival
from ..schemas.mail import (
    SendMailBatchRequest,
    SendMailBatchResponse,
    MailSendResult,
)
from ..services.email_service import send_html_email, EmailError
from ..services.mail_template_service import (
    interpolate,
    generate_personal_schedule_pdf,
    load_volunteer_with_jobs,
)
from ..models.volunteer import Volunteer
from .. import models

router = APIRouter(prefix="/mail", tags=["Mail"])


# ── Envoi d'un seul mail (bloquant, dans un thread pool) ─────────────────────

def _send_one(
    volunteer_id: UUID,
    subject_template: str,
    body_template: str,
    db: Session,
    include_schedule: bool = True,
    all_volunteers: list | None = None,
    assignments_by_job: dict | None = None,
) -> MailSendResult:
    """
    Charge le bénévole, interpole le template, génère le planning
    et envoie l'email. Retourne un MailSendResult.
    """
    volunteer = None
    try:
        volunteer, jobs = load_volunteer_with_jobs(db, volunteer_id)
        festival = get_festival(db)

        subject = interpolate(subject_template, volunteer, jobs, festival)
        body    = interpolate(body_template,    volunteer, jobs, festival)

        # Pièce jointe conditionnelle
        attachment_bytes = None
        filename         = None
        if include_schedule:
            attachment_bytes = generate_personal_schedule_pdf(
                volunteer=volunteer,
                jobs=jobs,
                festival=festival,
                all_volunteers=all_volunteers,
                assignments_by_job=assignments_by_job,
            )
            filename = f"planning_{volunteer.first_name}_{volunteer.last_name}.pdf"

        send_html_email(
            to_email=str(volunteer.email),
            subject=subject,
            html_body=body,
            attachment_bytes=attachment_bytes,
            attachment_filename=filename,
        )

        return MailSendResult(
            volunteer_id=volunteer_id,
            email=str(volunteer.email),
            success=True,
        )

    except ValueError as e:
        print(traceback.format_exc())
        return MailSendResult(
            volunteer_id=volunteer_id,
            email="inconnu",
            success=False,
            error=str(e),
        )
    except EmailError as e:
        print(traceback.format_exc())
        return MailSendResult(
            volunteer_id=volunteer_id,
            email=str(volunteer.email) if volunteer else "inconnu",
            success=False,
            error=str(e),
        )
    except Exception as e:
        print(traceback.format_exc())
        return MailSendResult(
            volunteer_id=volunteer_id,
            email=str(volunteer.email) if volunteer else "inconnu",
            success=False,
            error=f"Erreur inattendue : {e}",
        )


# ── Endpoint ──────────────────────────────────────────────────────────────────

@router.post("/send-batch", response_model=SendMailBatchResponse)
async def send_batch(
    payload: SendMailBatchRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Envoie un mail personnalisé à chaque bénévole de la liste.

    - Le sujet et le corps peuvent contenir des variables template ({{prenom}}, etc.)
    - Chaque bénévole reçoit son planning personnel en pièce jointe (PDF)
    - La colonne équipe du planning affiche tous les co-bénévoles sur chaque poste
    - Les envois sont effectués en parallèle (ThreadPoolExecutor)
    - Retourne un rapport détaillé succès / échecs
    """
    if not payload.recipient_ids:
        raise HTTPException(status_code=422, detail="La liste des destinataires est vide.")

    # ── Pré-chargement des données partagées (une seule requête pour tous) ────
    all_volunteers: list[Volunteer] | None = None
    assignments_by_job: dict[int, list] | None = None

    if payload.include_schedule:
        all_volunteers = db.query(Volunteer).all()

        all_assignments = db.query(models.Assignment).all()
        grouped: dict[int, list] = defaultdict(list)
        for a in all_assignments:
            grouped[a.job_id].append(a)
        assignments_by_job = dict(grouped)

    # ── Envoi en parallèle ────────────────────────────────────────────────────
    loop = asyncio.get_event_loop()

    def run_all() -> list[MailSendResult]:
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(
                    _send_one,
                    vid,
                    payload.subject,
                    payload.body_html,
                    db,
                    payload.include_schedule,
                    all_volunteers,
                    assignments_by_job,
                )
                for vid in payload.recipient_ids
            ]
        return [f.result() for f in futures]

    results = await loop.run_in_executor(None, run_all)

    success_count = sum(1 for r in results if r.success)
    error_count   = len(results) - success_count

    return SendMailBatchResponse(
        total=len(results),
        success=success_count,
        errors=error_count,
        results=results,
    )


# ── Endpoint de test de configuration SMTP ───────────────────────────────────

@router.post("/test-smtp", status_code=200)
def test_smtp(
    current_user=Depends(get_current_user),
):
    """
    Envoie un email de test à l'adresse de l'utilisateur connecté
    pour vérifier la configuration SMTP.
    """
    try:
        send_html_email(
            to_email=current_user.email,
            subject="✅ Test SMTP — Configuration OK",
            html_body="<p>Bonjour,<br/>Ce mail confirme que la configuration SMTP est correcte.</p>",
        )
        return {"message": f"Email de test envoyé à {current_user.email}"}
    except EmailError as e:
        raise HTTPException(status_code=500, detail=str(e))