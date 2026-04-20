"""
Étape 3 — Lancement de l'algorithme génétique.
"""
import logging
import sys
from typing import Any

from horizons_genetic.genetic.core.chromosome import Chromosome
from horizons_genetic.genetic.engine import GeneticEngine
from horizons_genetic.genetic.settings.config import GeneticConfig
from horizons_genetic.genetic.fitness.fitness_weights import GradualFitnessWeights

logger = logging.getLogger(__name__)


def run_genetic(
    postes: list[Any],
    benevoles: list[Any],
    params: GeneticConfig,
    on_progress=None
) -> tuple[Chromosome, GeneticEngine]:
    """Lance l'algorithme génétique et retourne la meilleure solution.

    Args:
        postes:    Liste des postes valides.
        benevoles: Liste des bénévoles valides.
        params:    Paramètres de l'algorithme (population, générations…).

    Returns:
        tuple (best_solution, engine) pour permettre l'accès aux méta-données
        de fitness en aval (notamment fitness_max_info).
    """

    logger.info("")
    logger.info("=" * 60)
    logger.info("ÉTAPE 3 — ALGORITHME GÉNÉTIQUE")
    logger.info("=" * 60)
    logger.info(f"  {len(postes)} poste(s)  |  {len(benevoles)} bénévole(s)")
    logger.info(f"  Population  : {params.population_size}")
    logger.info(f"  Générations : {params.generations}")
    logger.info(f"  Mutation    : {params.mutation_rate}")
    logger.info(f"  Élite       : {params.elite_count}")
    logger.info(f"  Tournoi     : {params.tournament_size}")

    weights = GradualFitnessWeights()
    config  = GeneticConfig(
        population_size=params.population_size,
        generations=params.generations,
        mutation_rate=params.mutation_rate,
        elite_count=params.elite_count,
        tournament_size=params.tournament_size,
        fitness_weights=weights,
    )

    try:
        engine = GeneticEngine(config, postes, benevoles, on_progress=on_progress)
        best_solution = engine.run()
    except Exception:
        logger.critical("Échec de l'algorithme génétique.", exc_info=True)
        sys.exit(1)

    return best_solution, engine