from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .. import models
from ..schemas.category import CategoryCreate, CategoryUpdate


def get_category(db: Session, category_id: int) -> models.Category | None:
    return db.query(models.Category).filter_by(id=category_id).first()


def get_categories(db: Session, skip: int = 0, limit: int = 100) -> list[models.Category]:
    return db.query(models.Category).offset(skip).limit(limit).all()


def get_or_create_category(db: Session, category_data: CategoryCreate) -> models.Category:
    existing = db.query(models.Category).filter_by(label=category_data.label).first()
    if existing:
        if existing.pole_id is None and category_data.pole_id is not None:
            existing.pole_id = category_data.pole_id
            db.flush()
            db.refresh(existing)
        return existing

    db_category = models.Category(
        label=category_data.label,
        pole_id=category_data.pole_id,
    )
    db.add(db_category)
    db.flush()
    db.refresh(db_category)
    return db_category


def create_category(db: Session, category: CategoryCreate) -> models.Category:
    db_category = models.Category(
        label=category.label,
        pole_id=category.pole_id,
        preference_id=category.preference_id,
    )
    db.add(db_category)
    db.flush()
    db.refresh(db_category)
    return db_category


def update_category(db: Session, category_id: int, payload: CategoryUpdate) -> models.Category | None:
    cat = db.query(models.Category).filter_by(id=category_id).first()
    if not cat:
        return None

    if payload.label         is not None: cat.label         = payload.label
    if payload.preference_id is not None: cat.preference_id = payload.preference_id
    if payload.pole_id       is not None: cat.pole_id       = payload.pole_id

    db.flush()
    db.refresh(cat)
    return cat


def delete_category(db: Session, category_id: int) -> bool:
    cat = get_category(db, category_id)
    if not cat:
        return False
    try:
        db.delete(cat)
        db.flush()
    except IntegrityError:
        db.rollback()
        raise
    return True