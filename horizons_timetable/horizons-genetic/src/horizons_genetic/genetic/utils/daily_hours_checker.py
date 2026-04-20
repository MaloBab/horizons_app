from horizons_core.dataclass.creneau import Creneau
from horizons_core.utils.enums import RecruitmentType
from horizons_genetic.genetic.fitness.fitness_weights import (
    MAX_HOURS_NORMAL,
    MAX_HOURS_SPECIALISE,
)
from horizons_genetic.genetic.utils.index_manager import IndexManager


def get_daily_limit(benevole_id: int, index_manager: IndexManager) -> int:
    """Retourne la limite horaire journalière du bénévole selon son type."""
    benevole = index_manager.id_to_benevole(benevole_id)
    if benevole is None:
        return MAX_HOURS_NORMAL
    if benevole.get_type_benevole() == RecruitmentType.SPECIALISE:
        return MAX_HOURS_SPECIALISE
    return MAX_HOURS_NORMAL


def compute_daily_hours(
    poste_to_benevoles: dict[int, list[int]],
    index_manager: IndexManager,
) -> dict[int, dict[int, float]]:
    """
    Calcule les heures travaillées par jour pour chaque bénévole.

    Returns:
        {benevole_id: {jour: heures_travaillees}}
    """
    daily_hours: dict[int, dict[int, float]] = {}

    for poste_id, benevole_ids in poste_to_benevoles.items():
        poste   = index_manager.id_to_poste(poste_id)
        creneau = poste.get_horaire()
        jour    = creneau.get_jour()
        duree   = creneau.get_borne_sup() - creneau.get_borne_inf()

        for b_id in benevole_ids:
            if b_id < 0:
                continue
            if b_id not in daily_hours:
                daily_hours[b_id] = {}
            daily_hours[b_id][jour] = daily_hours[b_id].get(jour, 0.0) + duree

    return daily_hours


def violates_daily_limit(
    benevole_id: int,
    creneau: Creneau,
    current_daily_hours: dict[int, dict[int, float]],
    index_manager: IndexManager,
) -> bool:
    """
    Vérifie si affecter ce bénévole à ce créneau violerait sa limite journalière.

    Args:
        benevole_id:         ID du bénévole à tester.
        creneau:             Créneau de la nouvelle affectation.
        current_daily_hours: Heures déjà comptabilisées {b_id: {jour: heures}}.
        index_manager:       Pour récupérer le type du bénévole.

    Returns:
        True si la limite serait dépassée, False sinon.
    """
    limit = get_daily_limit(benevole_id, index_manager)
    jour  = creneau.get_jour()
    duree = creneau.get_borne_sup() - creneau.get_borne_inf()

    current = current_daily_hours.get(benevole_id, {}).get(jour, 0.0)
    return (current + duree) > limit


def compute_daily_violation_penalty(
    poste_to_benevoles: dict[int, list[int]],
    index_manager: IndexManager,
    weights,
) -> float:
    """
    Calcule la pénalité totale pour toutes les violations de limites
    horaires journalières présentes dans un chromosome.

    Args:
        poste_to_benevoles: Structure du chromosome léger.
        index_manager:      Pour résoudre les IDs en objets domaine.
        weights:            GradualFitnessWeights (fournit violation_horaire_par_heure
                            et calculate_daily_violation_penalty).

    Returns:
        float ≤ 0 — somme des pénalités de violation (0 si aucune violation).

    Exemples :
        Aucune violation          → 0.0
        1 bénévole normal, +1h   → -2 000.0
        2 bénévoles, +1h chacun  → -4 000.0
        1 spécialisé, +0.5h      → -1 000.0
    """
    daily_hours = compute_daily_hours(poste_to_benevoles, index_manager)
    total_penalty = 0.0

    for b_id, hours_by_day in daily_hours.items():
        limit = get_daily_limit(b_id, index_manager)
        for jour, heures in hours_by_day.items():
            excess = heures - limit
            if excess > 0.0:
                total_penalty += weights.calculate_daily_violation_penalty(excess)

    return total_penalty