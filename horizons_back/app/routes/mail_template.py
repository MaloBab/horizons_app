from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..core.security import get_current_user
from ..crud import mail_template as crud
from ..schemas.mail_template import MailTemplateCreate, MailTemplateOut, MailTemplateUpdate

router = APIRouter(prefix="/mail-templates", tags=["Mail Templates"])


@router.get("/", response_model=list[MailTemplateOut])
def list_templates(
    skip: int = 0,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Retourne tous les templates de mail (admin uniquement)."""
    return crud.get_all(db, skip=skip)


@router.get("/{template_id}", response_model=MailTemplateOut)
def get_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Retourne un template par son ID."""
    template = crud.get(db, template_id)
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template introuvable")
    return template


@router.post("/", response_model=MailTemplateOut, status_code=status.HTTP_201_CREATED)
def create_template(
    data: MailTemplateCreate,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Crée un nouveau template de mail."""
    return crud.create(db, data)


@router.put("/{template_id}", response_model=MailTemplateOut)
def update_template(
    template_id: UUID,
    data: MailTemplateUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Met à jour un template existant (champs partiels acceptés)."""
    template = crud.update(db, template_id, data)
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template introuvable")
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_user),
):
    """Supprime un template."""
    success = crud.delete(db, template_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template introuvable")