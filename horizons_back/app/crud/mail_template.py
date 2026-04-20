# app/crud/mail_template.py

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ..models.mail_template import MailTemplate
from ..schemas.mail_template import MailTemplateCreate, MailTemplateUpdate


def get(db: Session, template_id: UUID) -> Optional[MailTemplate]:
    return db.query(MailTemplate).filter(MailTemplate.id == template_id).first()


def get_all(db: Session, skip: int = 0) -> list[MailTemplate]:
    return (
        db.query(MailTemplate)
        .order_by(MailTemplate.created_at.desc())
        .offset(skip)
        .all()
    )


def create(db: Session, data: MailTemplateCreate) -> MailTemplate:
    template = MailTemplate(**data.model_dump())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def update(db: Session, template_id: UUID, data: MailTemplateUpdate) -> Optional[MailTemplate]:
    template = get(db, template_id)
    if template is None:
        return None
    patch = data.model_dump(exclude_unset=True)
    for field, value in patch.items():
        setattr(template, field, value)
    setattr(template, 'updated_at', datetime.now(timezone.utc))
    db.commit()
    db.refresh(template)
    return template


def delete(db: Session, template_id: UUID) -> bool:
    template = get(db, template_id)
    if template is None:
        return False
    db.delete(template)
    db.commit()
    return True