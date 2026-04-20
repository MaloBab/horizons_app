from horizons_genetic.genetic.core.chromosome import Chromosome
from horizons_genetic.genetic.utils.index_manager import IndexManager
from horizons_genetic.genetic.core.chromosome import LightweightChromosome


class ChromosomeConverter:
    """
    Convertit entre représentations lourdes et légères.
    
    UTILISATION:
    - Initialisation et export: Heavy (objets)
    - Évolution génétique: Light (indices)
    """
    
    def __init__(self, index_manager: IndexManager):
        self.index_manager = index_manager
    
    def to_heavy(self, light_chromosome: LightweightChromosome) -> Chromosome:
        """Convertit LightweightChromosome → Chromosome."""
        affectations = {}
        
        for poste_id, benevole_ids in light_chromosome.poste_to_benevoles.items():
            poste = self.index_manager.id_to_poste(poste_id)
            benevoles = [
                self.index_manager.id_to_benevole(b_id) if b_id >= 0 else None
                for b_id in benevole_ids
            ]
            affectations[poste] = benevoles
        
        chromosome = Chromosome(affectations=affectations)
        fitness = light_chromosome.get_fitness()
        if fitness is not None:
            chromosome.set_fitness(
                fitness,
                light_chromosome.get_raw_scores()
            )
        
        return chromosome