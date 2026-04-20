"""
schemas/mail.py
Schémas Pydantic pour l'endpoint d'envoi de mails bénévoles.
"""
from __future__ import annotations

from pydantic import BaseModel, EmailStr
from uuid import UUID


# ── Payload entrant ───────────────────────────────────────────────────────────

class MailRecipient(BaseModel):
    """Un destinataire identifié par son UUID (on va chercher son planning en base)."""
    volunteer_id: UUID


class SendMailBatchRequest(BaseModel):
    """
    Corps de la requête POST /mail/send-batch.

    subject  : Objet du mail (peut contenir {{prenom}}, {{nom}}).
    body_html: Corps du mail en HTML (peut contenir toutes les variables template).
    recipient_ids: Liste des UUIDs des bénévoles à contacter.
    """
    subject:       str
    body_html:     str
    recipient_ids: list[UUID]
    include_schedule: bool = True


# ── Résultats renvoyés ────────────────────────────────────────────────────────

class MailSendResult(BaseModel):
    """Résultat d'un envoi individuel."""
    volunteer_id: UUID
    email:        str
    success:      bool
    error:        str | None = None


class SendMailBatchResponse(BaseModel):
    """Réponse globale de l'endpoint batch."""
    total:   int
    success: int
    errors:  int
    results: list[MailSendResult]