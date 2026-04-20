from typing import Optional
import random
from horizons_genetic.genetic.core.chromosome import LightweightChromosome


class LightweightPopulation:
    """
    Gère une population de LightweightChromosomes.

    Workflow GA conventionnel :
      - sort_by_fitness()     : tri décroissant (meilleur en tête)
      - get_best(n)           : accès aux n meilleurs individus (élitisme)
      - tournament_select()   : sélection par tournoi (pression de sélection)

    Les individus non encore évalués (fitness = None) sont traités comme
    les moins bons possibles lors du tri et de la sélection, ce qui garantit
    que seuls les individus évalués sont sélectionnés comme parents.
    """

    def __init__(self, chromosomes: Optional[list[LightweightChromosome]] = None):
        self._chromosomes: list[LightweightChromosome] = chromosomes or []
        self._sorted = False

    def add(self, chromosome: LightweightChromosome) -> None:
        self._chromosomes.append(chromosome)
        self._sorted = False

    def extend(self, chromosomes: list[LightweightChromosome]) -> None:
        self._chromosomes.extend(chromosomes)
        self._sorted = False

    @staticmethod
    def _fitness_key(c: LightweightChromosome) -> float:
        fitness = c.get_fitness()
        return fitness if fitness is not None else float('-inf')

    def sort_by_fitness(self, reverse: bool = True) -> None:
        # Les individus non évalués (None) sont classés en dernier
        # via le fallback float('-inf'), ce qui est le comportement
        # attendu dans un GA conventionnel (on ne sélectionne que
        # des individus évalués comme parents).
        self._chromosomes.sort(key=self._fitness_key, reverse=reverse)
        self._sorted = True

    def get_best(self, n: int = 1) -> list[LightweightChromosome]:
        if not self._sorted:
            self.sort_by_fitness()
        return self._chromosomes[:n]

    def size(self) -> int:
        return len(self._chromosomes)

    def tournament_select(self, tournament_size: int = 5) -> LightweightChromosome:
        tournament = random.sample(self._chromosomes, min(tournament_size, self.size()))
        return max(tournament, key=self._fitness_key)

    def clear(self) -> None:
        self._chromosomes.clear()
        self._sorted = False

    def __len__(self) -> int:
        return len(self._chromosomes)

    def __iter__(self):
        return iter(self._chromosomes)