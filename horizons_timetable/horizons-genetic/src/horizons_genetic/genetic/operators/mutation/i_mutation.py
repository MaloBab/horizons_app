from typing import Protocol
from horizons_genetic.genetic.core.chromosome import LightweightChromosome


class MutationOperator(Protocol):
    """Interface pour les opérateurs de mutation."""
    
    def mutate(self, chromosome: LightweightChromosome) -> LightweightChromosome:
        """Applique une mutation au chromosome donné."""
        ...

