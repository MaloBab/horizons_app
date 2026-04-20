from typing import Protocol

import logging

from horizons_genetic.genetic.core.chromosome import Chromosome, LightweightChromosome


logger = logging.getLogger(__name__)


class CrossoverOperator(Protocol):
    """Interface pour les opérateurs de crossover."""
    
    def crossover(self, parent1: LightweightChromosome, parent2: LightweightChromosome) -> LightweightChromosome:
        """Crée un enfant à partir de deux parents."""
        ...

