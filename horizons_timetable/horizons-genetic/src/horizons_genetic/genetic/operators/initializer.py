"""
Initialisation hybride de la population : greedy + semi-random + random.

Chaque stratégie respecte les CONTRAINTES DURES dès la création :
  - Pas de conflit horaire pour un bénévole
  - Limite journalière respectée (NORMAL : 6h, SPÉCIALISÉ : 2h)
"""
import logging
import random

from horizons_core.dataclass.creneau import Creneau
from horizons_core.dataclass.poste import Poste
from horizons_core.dataclass.benevole import Benevole

from horizons_genetic.genetic.core.chromosome import LightweightChromosome
from horizons_genetic.genetic.core.population import LightweightPopulation
from horizons_genetic.genetic.utils.index_manager import IndexManager
from horizons_genetic.genetic.fitness.affectation_scorer import score_affectation
from horizons_genetic.genetic.utils.daily_hours_checker import (
    violates_daily_limit,
    compute_daily_hours,
)

logger = logging.getLogger(__name__)


class PopulationInitializer:
    """
    Crée une population initiale valide (contraintes dures garanties).

    Répartition :
      - 50 % greedy      : postes difficiles d'abord, meilleurs candidats
      - 30 % semi-random : mélange greedy / aléatoire
      - 20 % random      : diversité pure
    """

    def __init__(
        self,
        postes:        list[Poste],
        benevoles:     list[Benevole],
        index_manager: IndexManager,
    ):
        self.postes        = postes
        self.benevoles     = benevoles
        self.index_manager = index_manager
        self._build_availability_cache()

    # ------------------------------------------------------------------

    def _build_availability_cache(self) -> None:
        """Pré-calcule pour chaque poste l'ensemble des bénévoles disponibles."""
        self.availability_cache: dict[int, set[int]] = {}
        for poste in self.postes:
            poste_id      = self.index_manager.poste_to_id(poste)
            available_ids = {
                self.index_manager.benevole_to_id(b)
                for b in self.benevoles
                if b.is_disponible(poste.get_horaire())
            }
            self.availability_cache[poste_id] = available_ids

    def initialize(self, population_size: int) -> LightweightPopulation:
        """Crée une population hybride de taille population_size."""
        population = LightweightPopulation()
        n_greedy   = int(population_size * 0.5)
        n_semi     = int(population_size * 0.3)
        n_random   = population_size - n_greedy - n_semi

        for _ in range(n_greedy):
            population.add(self._create_greedy_chromosome())

        for _ in range(n_semi):
            population.add(self._create_semi_random_chromosome())

        for _ in range(n_random):
            population.add(self._create_random_chromosome())

        logger.info(f"Population initiale créée : {population_size} chromosomes")
        return population

    # ------------------------------------------------------------------

    def _create_greedy_chromosome(self) -> LightweightChromosome:
        """Affecte les meilleurs candidats, postes les plus contraints en premier."""
        postes_sorted = sorted(
            self.postes,
            key=lambda p: len(self.availability_cache[self.index_manager.poste_to_id(p)]),
        )
        return self._fill_chromosome(postes_sorted, greedy_prob=0.8)

    def _create_semi_random_chromosome(self) -> LightweightChromosome:
        """Mélange greedy et aléatoire."""
        postes_shuffled = self.postes.copy()
        random.shuffle(postes_shuffled)
        return self._fill_chromosome(postes_shuffled, greedy_prob=0.5)

    def _create_random_chromosome(self) -> LightweightChromosome:
        """Affectation purement aléatoire (diversité)."""
        postes_shuffled = self.postes.copy()
        random.shuffle(postes_shuffled)
        return self._fill_chromosome(postes_shuffled, greedy_prob=0.0)

    # ------------------------------------------------------------------

    def _fill_chromosome(
        self,
        postes_ordered: list[Poste],
        greedy_prob:    float,
    ) -> LightweightChromosome:
        """
        Crée un chromosome en respectant les contraintes dures :
          1. Pas de conflit horaire
          2. Limite journalière selon le type de bénévole
        """
        poste_to_benevoles: dict[int, list[int]]      = {}
        daily_hours:        dict[int, dict[int, float]] = {}
        occupied_creneaux:  dict[int, list[Creneau]]   = {}

        for poste in postes_ordered:
            poste_id = self.index_manager.poste_to_id(poste)
            creneau  = poste.get_horaire()

            candidates = [
                b_id for b_id in self.availability_cache[poste_id]
                if not self._has_time_conflict(b_id, creneau, occupied_creneaux)
                and not violates_daily_limit(b_id, creneau, daily_hours, self.index_manager)
            ]

            if greedy_prob > 0 and random.random() < greedy_prob:
                # Tri par score (bug préférences corrigé via score_affectation)
                candidates = sorted(
                    candidates,
                    key=lambda b_id: score_affectation(b_id, poste_id, self.index_manager),
                    reverse=True,
                )

            selected: list[int] = []
            for b_id in candidates:
                if len(selected) >= poste.get_size():
                    break
                selected.append(b_id)
                occupied_creneaux.setdefault(b_id, []).append(creneau)
                jour  = creneau.get_jour()
                duree = creneau.get_borne_sup() - creneau.get_borne_inf()
                if b_id not in daily_hours:
                    daily_hours[b_id] = {}
                daily_hours[b_id][jour] = daily_hours[b_id].get(jour, 0.0) + duree

            while len(selected) < poste.get_size():
                selected.append(-1)

            poste_to_benevoles[poste_id] = selected

        return LightweightChromosome(poste_to_benevoles=poste_to_benevoles)

    # ------------------------------------------------------------------

    def _has_time_conflict(
        self,
        benevole_id:       int,
        creneau:           Creneau,
        occupied_creneaux: dict[int, list[Creneau]],
    ) -> bool:
        return any(
            creneau.is_incompatible(c)
            for c in occupied_creneaux.get(benevole_id, [])
        )