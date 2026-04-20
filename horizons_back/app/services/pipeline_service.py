"""
services/pipeline_service.py

Convertit les données DB en objets horizons_core, lance l'algorithme génétique
et persiste les affectations résultantes.
"""
from __future__ import annotations
from sqlalchemy.orm import Session, joinedload

from .. import models
from ..crud.assignment import replace_all_assignments
from horizons_core.dataclass.benevole import Benevole
from horizons_core.dataclass.categorie import Categorie
from horizons_core.dataclass.creneau import Creneau
from horizons_core.dataclass.poste import Poste
from horizons_core.utils.enums import RecruitmentType
from horizons_core.utils.enums import Pole
from horizons_genetic.launch.genetic import run_genetic
from horizons_genetic.genetic.settings.config import GeneticConfig



# ── Chargement & conversion ───────────────────────────────────────────────────

def _load_postes(db: Session) -> list[Poste]:
    """Charge tous les jobs de type NORMAL et les convertit en Poste."""
    jobs = (
        db.query(models.Job)
        .options(
            joinedload(models.Job.category),
            joinedload(models.Job.slot),
        )
        .filter(models.Job.recruitment_type == models.job.RecruitmentType.Normal)
        .all()
    )

    postes = []
    for job in jobs:
        categorie = Categorie(
            nom=job.category.label,
            pole_id= Pole(job.category.pole_id) if job.category and job.category.pole_id else Pole.AUTRES,
        )
        creneau = Creneau(
            borne_inf=job.slot.start_time,
            borne_sup=job.slot.end_time,
            jour=job.slot.day_index,
        )
        poste = Poste(
            nom=job.name,
            categorie=categorie,
            type_benevole=RecruitmentType.NORMAL,
            horaire=creneau,
            size=job.required_volunteers,
            responsible=job.responsible,
        )
        # On attache l'id DB pour retrouver le job après l'algo
        poste.set_id(job.id)
        postes.append(poste)

    return postes


def _load_benevoles(db: Session) -> list[Benevole]:
    """Charge tous les bénévoles et les convertit en objets Benevole."""
    volunteers = (
        db.query(models.Volunteer)
        .options(
            joinedload(models.Volunteer.slots).joinedload(models.volunteer.VolunteerSlot.slot),
            joinedload(models.Volunteer.preferences)
                .joinedload(models.volunteer.VolunteerPreference.preference),
            joinedload(models.Volunteer.mates),
        )
        .all()
    )

    # Première passe : création des objets sans compagnons
    benevole_by_id: dict[str, Benevole] = {}
    db_vol_by_id:   dict[str, models.Volunteer] = {}

    for vol in volunteers:
        dispos = [
            Creneau(
                borne_inf=vs.slot.start_time,
                borne_sup=vs.slot.end_time,
                jour=vs.slot.day_index,
            )
            for vs in vol.slots
        ]

        prefs = [
            vp.preference.label.lower()
            for vp in sorted(vol.preferences, key=lambda p: p.rank)
        ]
        
        volunteer_type = vol.volunteer_type

        benevole = Benevole(
            nom=str(vol.last_name).lower(),
            prenom=str(vol.first_name).lower(),
            mail=str(vol.email),
            adresse=str(vol.address),
            numero_tel=str(vol.phone_number),
            disponibilites=dispos,
            preferences=prefs,
            type_benevole= RecruitmentType(volunteer_type),
        )
        benevole.set_id(str(vol.id))

        benevole_by_id[str(vol.id)] = benevole
        db_vol_by_id[str(vol.id)]   = vol

    # Deuxième passe : lien compagnons (bidirectionnel)
    for vol in volunteers:
        b = benevole_by_id[str(vol.id)]
        for mate in vol.mates:
            mate_obj = benevole_by_id.get(str(mate.id))
            if mate_obj:
                b.add_compagnon(mate_obj)

    return list(benevole_by_id.values())


# ── Point d'entrée principal ──────────────────────────────────────────────────

def run_pipeline(db: Session, on_progress=None) -> list[models.Assignment]:
    postes    = _load_postes(db)
    benevoles = _load_benevoles(db)

    if not postes or not benevoles:
        raise ValueError(
            f"Données insuffisantes : {len(postes)} poste(s), {len(benevoles)} bénévole(s)."
        )
    
    
    best_solution, _ = run_genetic(postes, benevoles, GeneticConfig(), on_progress=on_progress)

    # ── DEBUG ─────────────────────────────────────────────────────────────────
    pairs: list[tuple] = []

    for poste, affectes in best_solution.affectations.items():
        job_id = poste.get_id()
        if job_id is None:
            continue
        for benevole in affectes:
            if benevole is None:
                continue
            volunteer_id = benevole.get_id()
            if volunteer_id is None:
                continue
            pairs.append((volunteer_id, job_id))

    return replace_all_assignments(db, pairs)