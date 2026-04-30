from dataclasses import dataclass, field

from horizons_genetic.genetic.fitness.fitness_weights import GradualFitnessWeights


@dataclass
class GeneticConfig:
    """
    Configuration de l'algorithme génétique.

    PARAMÈTRES OPTIMISÉS RASPBERRY PI 4 Go :
      - population_size réduite à 300 (vs 1000 original) pour limiter la RAM.
        La réduction est compensée par plus de générations (800 vs 500).
      - stagnation_limit augmenté à 150 pour ne pas couper trop tôt.
      - immigration plus agressive (_IMMIGRATION_RATE=0.12 dans engine.py).

    Paramètres clés du workflow :
      population_size  : Nombre d'individus par génération (taille constante).
      generations      : Nombre maximum de générations.
      elite_count      : Nombre d'élites garantis survivants à chaque génération.
      crossover_rate   : Proportion de la population sélectionnée pour se reproduire.
      mutation_rate    : Probabilité qu'un enfant soit muté après le crossover.
      tournament_size  : Taille du tournoi pour la sélection des parents.
      stagnation_limit : Générations sans amélioration avant arrêt anticipé.
    """

    population_size:  int   = 300
    generations:      int   = 800
    elite_count:      int | None = field(default=None)
    crossover_rate:   float = 0.65
    mutation_rate:    float = 0.08
    tournament_size:  int   = 7
    stagnation_limit: int   = 150
    fitness_weights:  GradualFitnessWeights | None = None

    def __post_init__(self):
        if self.fitness_weights is None:
            self.fitness_weights = GradualFitnessWeights()

        if self.elite_count is None:
            # ~3.3 % de la population, minimum 5
            self.elite_count = max(5, self.population_size // 30)

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