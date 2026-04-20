"""
Service d'import — orchestre parsing → validation → persistance.
Stratégie : backup → delete → import → commit ou rollback vers backup
"""
import json
import pprint
import traceback
from sqlalchemy.orm import Session, joinedload

from parsing_poste.parseur_poste import ParseurPoste
from parsing_poste.settings.poste_config import PosteConfig

from .. import crud, models
from ..schemas.job import JobCreate, JobResponse
from ..schemas.category import CategoryCreate
from ..schemas.slot import SlotCreate
from ..schemas.import_job_report import ImportReport, ImportWarning, ImportError


ALLOWED_EXTENSIONS = {".ods"}


def import_postes_from_file(filepath: str, db: Session) -> ImportReport:
    """Parse un fichier ODS, remplace tous les postes existants.

    Stratégie transactionnelle :
    1. Snapshot des postes + catégories existants (backup en mémoire)
    2. Suppression de tout (sauf slots)
    3. Parsing + insertion des nouveaux postes
    4a. Aucune erreur critique → commit
    4b. Erreur critique → rollback manuel (réinsère le backup)

    Args:
        filepath: Chemin vers le fichier temporaire uploadé.
        db: Session SQLAlchemy (injectée par FastAPI).

    Returns:
        ImportReport avec le détail des postes persistés, warnings et erreurs.
    """
    # ── 1. Backup en mémoire ────────────────────────────────────────────────
    backup = _snapshot(db)

    # ── 2. Suppression jobs (slots et catégories conservés) ─────────────────
    try:
        _delete_all(db)
        db.flush()
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Erreur lors de la suppression initiale : {e}") from e

    # ── 3. Parsing ──────────────────────────────────────────────────────────
    # parse_all() retourne directement list[ParseResult] — pas de json.loads nécessaire
    config        = PosteConfig(row_max=150)
    parseur       = ParseurPoste(filepath, config=config)
    parse_results = parseur.parse_all()

    # Groupement par (nom, pole_id) : même logique que to_json() mais on
    # travaille directement sur les objets domaine pour éviter une
    # sérialisation/désérialisation inutile.

    grouped: dict[tuple, dict] = {}
    invalids_raw: list         = []
    sort_counter               = 0

    for result in parse_results:
        if not result.is_valid or result.entity is None:
            invalids_raw.append(result)
            continue

        poste    = result.entity
        horaire  = poste.get_horaire()
        categorie = poste.get_categorie()
        key = (poste.get_nom(), categorie.nom, categorie.pole_id, poste.get_type().value)

        if key not in grouped:
            grouped[key] = {
                "is_valid":  True,
                "ligne":     result.ligne,
                "warnings":  result.warnings,
                "entity": {
                    "name":             poste.get_nom(),
                    "recruitment_type": poste.get_type().value,
                    "responsible":      poste.get_responsible(),
                    "sort_order":       sort_counter,
                    "category": {
                        "label":   categorie.nom,
                        "pole_id": categorie.pole_id,
                    },
                    "slots": [],
                },
            }
            sort_counter += 1

        grouped[key]["entity"]["slots"].append({
            "day_index":           horaire.get_jour(),
            "start_time":          horaire.get_borne_inf(),
            "end_time":            horaire.get_borne_sup(),
            "required_volunteers": poste.get_size(),
        })
        
    for k, v in grouped.items():
        print(repr(k), "→", len(v["entity"]["slots"]), "slots")

    persisted_jobs: list[models.Job] = []
    warnings: list[ImportWarning]    = []
    errors: list[ImportError]        = []

    # — Erreurs issues des ParseResult invalides —
    for result in invalids_raw:
        ligne = result.ligne
        for err in result.errors:
            errors.append(ImportError(
                ligne=ligne,
                nom="",
                message=err.message,
            ))
        for w in result.warnings:
            warnings.append(ImportWarning(
                ligne=ligne,
                nom="",
                message=w.message,
            ))

    try:        
        for group in grouped.values():
            entity = group["entity"]
            ligne  = group["ligne"]

            # — Warnings non bloquants sur un poste valide —
            for w in group["warnings"]:
                warnings.append(ImportWarning(
                    ligne=ligne,
                    nom=entity["name"],
                    message=w.message,
                ))

            # — Persistance — 1 entity groupée = N slots —
            for slot_data in entity["slots"]:
                job_create = JobCreate(
                    name=entity["name"],
                    required_volunteers=slot_data["required_volunteers"],
                    recruitment_type=entity["recruitment_type"],
                    responsible=entity.get("responsible"),
                    sort_order=entity.get("sort_order", 0),
                    category=CategoryCreate(
                        label=entity["category"]["label"],
                        pole_id=entity["category"].get("pole_id"),
                    ),
                    slot=SlotCreate(
                        day_index=slot_data["day_index"],
                        start_time=slot_data["start_time"],
                        end_time=slot_data["end_time"],
                    ),
                )

                category = crud.category.get_or_create_category(db, job_create.category)
                slot     = crud.slot.get_or_create_slot(db, job_create.slot)
                db_job   = crud.job.create_job(db, job_create, category.id, slot.id)
                persisted_jobs.append(db_job)

        # ── 4a. Commit ───────────────────────────────────────────────────────
        db.commit()

        job_ids   = [j.id for j in persisted_jobs]
        full_jobs = (
            db.query(models.Job)
            .options(joinedload(models.Job.category), joinedload(models.Job.slot))
            .filter(models.Job.id.in_(job_ids))
            .all()
        )
        persisted_responses = [JobResponse.model_validate(j) for j in full_jobs]

    except Exception as e:
        # ── 4b. Rollback + restauration backup ───────────────────────────────
        traceback.print_exc()
        db.rollback()
        try:
            _restore(db, backup)
            db.commit()
        except Exception as restore_err:
            db.rollback()
            raise RuntimeError(
                f"Erreur import ET échec restauration backup : {restore_err}"
            ) from restore_err
        raise RuntimeError(
            f"Erreur lors de la persistance, anciens postes restaurés : {e}"
        ) from e

    return ImportReport(
        persisted=persisted_responses,
        warnings=warnings,
        errors=errors,
        total_parsed=len(parse_results),
        total_persisted=len(persisted_responses),
        total_warnings=len(warnings),
        total_errors=len(errors),
    )


# ── Helpers backup/restore ───────────────────────────────────────────────────

def _snapshot(db: Session) -> dict:
    """Capture l'état actuel en mémoire avant toute modification."""
    jobs = (
        db.query(models.Job)
        .options(joinedload(models.Job.category), joinedload(models.Job.slot))
        .all()
    )
    return {
        "jobs": [
            {
                "name":                j.name,
                "required_volunteers": j.required_volunteers,
                "recruitment_type":    j.recruitment_type,
                "responsible":         j.responsible,
                "sort_order":          j.sort_order,
                "category": {
                    "label":   j.category.label   if j.category else "Inconnu",
                    "pole_id": j.category.pole_id if j.category else None,
                },
                "slot": {
                    "day_index":  j.slot.day_index,
                    "start_time": j.slot.start_time,
                    "end_time":   j.slot.end_time,
                },
            }
            for j in jobs
        ]
    }


def _delete_all(db: Session) -> None:
    """Supprime tous les jobs — slots et catégories conservés."""
    db.query(models.assignment.Assignment).delete(synchronize_session=False)
    db.query(models.Job).delete(synchronize_session=False)


def _restore(db: Session, backup: dict) -> None:
    """Réinsère les données du backup après un rollback."""
    for job_data in backup["jobs"]:
        category = crud.category.get_or_create_category(
            db, CategoryCreate(
                label=job_data["category"]["label"],
                pole_id=job_data["category"]["pole_id"],
            )
        )
        slot = crud.slot.get_or_create_slot(
            db, SlotCreate(**job_data["slot"])
        )
        job_create = JobCreate(
            name=job_data["name"],
            required_volunteers=job_data["required_volunteers"],
            recruitment_type=job_data["recruitment_type"],
            responsible=job_data.get("responsible"),
            sort_order=job_data.get("sort_order", 0),
            category=CategoryCreate(
                label=job_data["category"]["label"],
                pole_id=job_data["category"]["pole_id"],
            ),
            slot=SlotCreate(**job_data["slot"]),
        )
        crud.job.create_job(db, job_create, category.id, slot.id)


def _extract_nom(message: str) -> str:
    """Extrait le nom du poste depuis un message de warning."""
    marker = "pour le poste "
    idx    = message.find(marker)
    return message[idx + len(marker):] if idx != -1 else "?"