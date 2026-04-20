from dataclasses import dataclass, field

from horizons_genetic.genetic.fitness.fitness_weights import GradualFitnessWeights


@dataclass
class GeneticConfig:
    """
    Configuration de l'algorithme génétique.

    Paramètres clés du workflow :
      population_size  : Nombre d'individus par génération (taille constante).
      generations      : Nombre maximum de générations.
      elite_count      : Nombre d'élites garantis survivants à chaque génération.
      crossover_rate   : Proportion de la population (hors élites) sélectionnée
                         pour se reproduire. Ex : 0.6 → 60 % se reproduisent,
                         40 % passent directement dans le pool de candidats.
      mutation_rate    : Probabilité qu'un enfant soit muté après le crossover.
      tournament_size  : Taille du tournoi pour la sélection des parents.
      stagnation_limit : Nombre de générations sans amélioration avant arrêt anticipé.

    """

    population_size:  int   = 600
    generations:      int   = 750
    elite_count:      int | None = field(default=None)
    crossover_rate:   float = 0.6
    mutation_rate:    float = 0.1
    tournament_size:  int   = 10
    stagnation_limit: int   = 100
    fitness_weights:  GradualFitnessWeights | None = None

    def __post_init__(self):
        if self.fitness_weights is None:
            self.fitness_weights = GradualFitnessWeights()
            
        if self.elite_count is None:
            self.elite_count = self.population_size // 20

        if not 0.0 < self.crossover_rate <= 1.0:
            raise ValueError(
                f"crossover_rate doit être dans ]0, 1] (reçu : {self.crossover_rate})"
            )
        if not 0.0 <= self.mutation_rate <= 1.0:
            raise ValueError(
                f"mutation_rate doit être dans [0, 1] (reçu : {self.mutation_rate})"
            )
        if self.elite_count >= self.population_size:
            raise ValueError(
                f"elite_count ({self.elite_count}) doit être < population_size ({self.population_size})"
            )