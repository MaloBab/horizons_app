"""
Étape 5 — Statistiques finales de la solution.

Ce module ne produit aucun effet de bord autre que du logging ;
tous les calculs sont isolés dans des fonctions pures.
"""
import logging
from collections import defaultdict
from typing import Any

from horizons_genetic.launch.config import MAX_HEURES_PAR_JOUR, MAX_OVERLOADED_LOGGED

logger = logging.getLogger(__name__)

_JOURS_LABELS = {0: "Vendredi", 1: "Samedi", 2: "Dimanche"}


# ---------------------------------------------------------------------------
# Calculs purs
# ---------------------------------------------------------------------------

def compute_benevole_hours(solution: Any) -> dict[Any, list[int]]:
    """Calcule le nombre d'heures travaillées par bénévole par jour.

    Returns:
        dict {benevole: [heures_vendredi, heures_samedi, heures_dimanche]}
    """
    benevole_hours: dict[Any, list[int]] = defaultdict(lambda: [0, 0, 0])

    for poste, affectes in solution.affectations.items():
        creneau    = poste.get_horaire()
        jour_index = creneau.get_jour() - 4          # jour 4=vendredi → index 0
        duration   = creneau.get_borne_sup() - creneau.get_borne_inf()

        if jour_index not in (0, 1, 2):
            continue

        for benevole in affectes:
            if benevole is None:
                continue
            benevole_hours[benevole][jour_index] += duration

    return dict(benevole_hours)


def find_overloaded(
    benevole_hours: dict[Any, list[int]],
    max_hours: int = MAX_HEURES_PAR_JOUR,
) -> list[Any]:
    """Retourne les bénévoles dépassant le seuil horaire sur au moins un jour."""
    return [b for b, hours in benevole_hours.items() if any(h > max_hours for h in hours)]


# ---------------------------------------------------------------------------
# Affichage
# ---------------------------------------------------------------------------

def log_statistics(solution: Any, benevoles: list[Any], engine: Any) -> None:
    """Étape 5 — Loggue les statistiques finales de la solution.

    Args:
        solution:  Meilleur chromosome après validation/réparation.
        benevoles: Liste complète des bénévoles (pour le calcul du taux).
        engine:    GeneticEngine (fournit fitness_max_info).
    """
    logger.info("")
    logger.info("=" * 60)
    logger.info("ÉTAPE 5 — STATISTIQUES FINALES")
    logger.info("=" * 60)

    _log_affectation_summary(solution, benevoles)
    _log_fitness(solution, engine)
    _log_raw_scores(solution)
    _log_overloaded(solution)


# ---------------------------------------------------------------------------
# Helpers privés
# ---------------------------------------------------------------------------

def _log_affectation_summary(solution: Any, benevoles: list[Any]) -> None:
    assigned = solution.get_assigned_benevoles()
    filled   = solution.count_filled_positions()
    total    = solution.count_total_positions()

    n_benevoles = len(benevoles)
    pct_benevoles = len(assigned) / n_benevoles * 100 if n_benevoles else 0.0
    pct_postes    = filled / total * 100 if total else 0.0

    logger.info(f"  Bénévoles affectés : {len(assigned)}/{n_benevoles} ({pct_benevoles:.1f}%)")
    if total:
        logger.info(f"  Postes remplis     : {filled}/{total} ({pct_postes:.1f}%)")
    else:
        logger.info("  Postes remplis     : aucun poste")


def _log_fitness(solution: Any, engine: Any) -> None:
    from horizons_genetic.genetic.fitness.max_fitness import format_fitness_percentage

    fitness = solution.get_fitness()
    if fitness is None:
        return

    fitness_str = format_fitness_percentage(fitness, engine.fitness_max_info)
    logger.info(f"  Fitness final      : {fitness_str}")


def _log_raw_scores(solution: Any) -> None:
    scores = solution.get_raw_scores()
    if not scores:
        return

    logger.info("")
    logger.info("  Détail des scores :")
    for criterion, score in sorted(scores.items()):
        logger.info(f"    {criterion:.<40} {score:>10.0f}")


def _log_overloaded(solution: Any) -> None:
    benevole_hours = compute_benevole_hours(solution)
    overloaded     = find_overloaded(benevole_hours)

    logger.info(f"\n  Bénévoles surchargés (>{MAX_HEURES_PAR_JOUR}h/jour) : {len(overloaded)}")
    if not overloaded:
        return

    for benevole in overloaded[:MAX_OVERLOADED_LOGGED]:
        hours = benevole_hours[benevole]
        depassements = [
            f"{_JOURS_LABELS[i]}: {hours[i]}h"
            for i in range(3)
            if hours[i] > MAX_HEURES_PAR_JOUR
        ]
        logger.warning(f"    {benevole.get_name()} — {', '.join(depassements)}")

    surplus = len(overloaded) - MAX_OVERLOADED_LOGGED
    if surplus > 0:
        logger.warning(f"    … et {surplus} autre(s)")