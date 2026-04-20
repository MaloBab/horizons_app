from sqlalchemy.orm import Session
from .. import models
from ..schemas.preference import PreferenceCreate


def get_preferences(db: Session) -> list[models.preference.Preference]:
    return db.query(models.preference.Preference).all()

def get_preference(db: Session, preference_id: int) -> models.preference.Preference | None:
    return db.query(models.preference.Preference).filter_by(id=preference_id).first()

def create_preference(db: Session, preference: PreferenceCreate) -> models.preference.Preference:
    db_preference = models.preference.Preference(label=preference.label)
    db.add(db_preference)
    db.commit()
    db.refresh(db_preference)
    return db_preference

def rename_preference(db: Session, preference_id: int, label: str) -> models.preference.Preference | None:
    pref = db.query(models.preference.Preference).filter_by(id=preference_id).first()
    if not pref:
        return None
    db.query(models.preference.Preference)\
      .filter_by(id=preference_id)\
      .update({"label": label})
    db.commit()
    db.refresh(pref)
    return pref

def delete_preference(db: Session, preference_id: int) -> bool:
    db_preference = db.query(models.preference.Preference).filter_by(id=preference_id).first()
    if not db_preference:
        return False
    db.delete(db_preference)
    db.commit()
    return True