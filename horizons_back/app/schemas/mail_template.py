# app/schemas/mail_template.py

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


# ── Création ──────────────────────────────────────────────────────────────────

class MailTemplateCreate(BaseModel):
    title: str = Field(..., max_length=255)
    subject: str = Field(..., max_length=255)
    content: str = Field(...)
    is_active: bool = True


# ── Mise à jour ──────────────────────────────────

class MailTemplateUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    subject: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    is_active: Optional[bool] = None


# ── Réponse API ───────────────────────────────────────────────────────────────

class MailTemplateOut(BaseModel):
    id: UUID
    title: str
    subject: str
    content: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}