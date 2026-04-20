"""
Service d'import bénévoles — orchestre parsing → validation → persistance.
Stratégie : backup → delete (flush) → import → commit ou rollback vers backup
"""
import traceback
from sqlalchemy.orm import Session, joinedload

from parsing_benevole.parseur_benevole import Benevole, ParseurBenevole

from .. import crud, models
from ..models.preference import Preference
from ..schemas.volunteer import VolunteerCreate, VolunteerResponse
from ..schemas.slot import SlotCreate
from ..schemas.import_volunteer_report import ImportReport, ImportWarning, ImportError
from ..crud.volunteer import create_volunteer, _delete_all_volunteers_flush, resolve_mates

ALLOWED_EXTENSIONS = {".ods"}


def _build_preference_label_map(db: Session) -> dict[str, int]:
    rows = db.query(Preference.id, Preference.label).all()
    return {str(label).lower().strip(): int(id_) for id_, label in rows}


def _resolve_preference_ids(
    raw_prefs: list,
    label_map: dict[str, int],
    warnings: list[ImportWarning],
    ligne: int,
    nom: str,
) -> list[int]:
    """Convertit une liste mixte (labels str ou ids int) en liste d'ids entiers."""
    ids: list[int] = []
    for pref in raw_prefs:
        if isinstance(pref, int):
            ids.append(pref)
        elif isinstance(pref, str):
            key = pref.lower().strip()
            if key in label_map:
                ids.append(label_map[key])
            else:
                warnings.append(ImportWarning(
                    ligne=ligne,
                    nom=nom,
                    message=f"Préférence inconnue ignorée : '{pref}'",
                ))
    return ids


def import_benevoles_from_file(filepath: str, db: Session) -> ImportReport:
    """Parse un fichier ODS, remplace tous les bénévoles existants."""

    # ── 1. Backup + index préférences ────────────────────────────────────────
    backup         = _snapshot(db)
    preference_map = _build_preference_label_map(db)

    # ── 2. Suppression sans commit ────────────────────────────────────────────
    try:
        _delete_all_volunteers_flush(db)
        db.flush()
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Erreur lors de la suppression initiale : {e}") from e

    # ── 3. Parsing ────────────────────────────────────────────────────────────
    # parse_all() retourne directement list[ParseResult] — pas de json.loads nécessaire.
    # Les warnings/errors sont des objets ParseError accessibles via .message, .severity, etc.
    parseur       = ParseurBenevole(filepath)
    parse_results = parseur.parse_all()

    persisted_volunteers: list[models.volunteer.Volunteer] = []
    warnings: list[ImportWarning] = []
    errors:   list[ImportError]   = []
    mate_emails_map: dict[str, list[str]] = {}

    try:
        for result in parse_results:
            ligne    = result.ligne
            benevole : Benevole | None = result.entity

            # — Erreurs critiques — le bénévole est ignoré —
            if not result.is_valid:
                for err in result.errors:
                    errors.append(ImportError(
                        ligne=ligne,
                        nom=_extract_nom_from_entity(benevole),
                        message=err.message,
                    ))
                continue

            if benevole is None:
                continue

            # — Warnings du parseur (créneaux, email, téléphone, adresse…) —
            for w in result.warnings:
                warnings.append(ImportWarning(
                    ligne=ligne,
                    nom=benevole.get_name(),
                    message=w.message,
                ))

            # — Résolution des préférences (labels → ids) —
            preference_ids = _resolve_preference_ids(
                benevole.get_preferences(),
                preference_map,
                warnings,
                ligne,
                benevole.get_name(),
            )

            # — Résolution des slots depuis les disponibilités —
            slot_ids: list[int] = []
            for creneau in benevole.get_disponibilites():
                slot = crud.slot.get_or_create_slot(db, SlotCreate(
                    day_index=creneau.get_jour(),
                    start_time=creneau.get_borne_inf(),
                    end_time=creneau.get_borne_sup(),
                ))
                slot_ids.append(slot.id)

            volunteer_create = VolunteerCreate(
                first_name=benevole.get_prenom().title(),
                last_name=benevole.get_nom().title(),
                email=benevole.get_mail(),
                address=benevole.get_adresse(),
                phone_number=benevole.get_numero_tel(),
                volunteer_type=benevole.get_type_benevole().value,
                preference_ids=preference_ids,
                slot_ids=slot_ids,
                availabilities=[
                    {
                        "day_index":  c.get_jour(),
                        "start_time": c.get_borne_inf(),
                        "end_time":   c.get_borne_sup(),
                    }
                    for c in benevole.get_disponibilites()
                ],
                mate_emails=benevole.get_compagnons_emails(),
            )

            db_volunteer = create_volunteer(db, volunteer_create)
            persisted_volunteers.append(db_volunteer)

            mate_emails = benevole.get_compagnons_emails()
            if mate_emails:
                mate_emails_map[benevole.get_mail()] = mate_emails

        # ── 4. Résolution des affinités ───────────────────────────────────────
        for volunteer_email, mates in mate_emails_map.items():
            resolve_mates(db, volunteer_email, mates)

        # ── 4a. Commit ────────────────────────────────────────────────────────
        db.commit()

        volunteer_ids   = [v.id for v in persisted_volunteers]
        full_volunteers = (
            db.query(models.volunteer.Volunteer)
            .options(
                joinedload(models.volunteer.Volunteer.preferences),
                joinedload(models.volunteer.Volunteer.slots),
                joinedload(models.volunteer.Volunteer.mates),
            )
            .filter(models.volunteer.Volunteer.id.in_(volunteer_ids))
            .all()
        )
        persisted_responses = [VolunteerResponse.model_validate(v) for v in full_volunteers]

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
            f"Erreur lors de la persistance, anciens bénévoles restaurés : {e}"
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


# ── Helpers ───────────────────────────────────────────────────────────────────

def _snapshot(db: Session) -> dict:
    volunteers = (
        db.query(models.volunteer.Volunteer)
        .options(
            joinedload(models.volunteer.Volunteer.preferences),
            joinedload(models.volunteer.Volunteer.slots),
            joinedload(models.volunteer.Volunteer.mates),
        )
        .all()
    )
    return {
        "volunteers": [
            {
                "first_name":     v.first_name,
                "last_name":      v.last_name,
                "email":          v.email,
                "address":        v.address,
                "phone_number":   v.phone_number,
                "volunteer_type": v.volunteer_type,
                "preference_ids": [
                    vp.preference_id
                    for vp in sorted(v.preferences, key=lambda p: p.rank)
                ],
                "slot_ids":    [vs.slot_id for vs in v.slots],
                "mate_emails": [m.email for m in v.mates],
            }
            for v in volunteers
        ]
    }


def _restore(db: Session, backup: dict) -> None:
    mate_emails_map: dict[str, list[str]] = {}

    for v_data in backup["volunteers"]:
        volunteer_create = VolunteerCreate(
            first_name=v_data["first_name"],
            last_name=v_data["last_name"],
            email=v_data["email"],
            address=v_data["address"],
            phone_number=v_data["phone_number"],
            volunteer_type=v_data["volunteer_type"],
            preference_ids=v_data["preference_ids"],
            slot_ids=v_data["slot_ids"],
            availabilities=[],
            mate_emails=v_data["mate_emails"],
        )
        create_volunteer(db, volunteer_create)

        if v_data["mate_emails"]:
            mate_emails_map[v_data["email"]] = v_data["mate_emails"]

    for volunteer_email, mates in mate_emails_map.items():
        resolve_mates(db, volunteer_email, mates)


def _extract_nom_from_entity(benevole) -> str:
    """Retourne le nom complet du bénévole ou '?' si absent."""
    if benevole is None:
        return "?"
    try:
        return benevole.get_name()
    except Exception:
        return "?"