"""
Moteur de l'algorithme génétique — v3.

AMÉLIORATIONS vs v2 :

1. SCORE CACHE PARTAGÉ
   ScoreCache est construit une seule fois dans __init__ et transmis à tous
   les opérateurs (initializer, crossover, mutation). Évite de recalculer
   disponibilité + préférences des millions de fois.

2. store_raw=False PENDANT L'ÉVOLUTION
   Les raw_scores (dict à 6 clés par chromosome) ne sont plus alloués pendant
   l'évolution. Seul le scalaire fitness est conservé. On ne stocke les
   raw_scores qu'une seule fois sur le meilleur individu final.
   → Réduit la pression GC sur Raspberry Pi.

3. HILL-CLIMBING POST-GÉNÉTIQUE (phase 3)
   Après la boucle évolutive, HillClimber affine le meilleur chromosome
   par perturbations unitaires (swap, fill, shift, preference) jusqu'à
   convergence locale. Gain typique : +2–5 % de fitness pour un coût
   mémoire quasi nul.

4. PARAMÈTRES PAR DÉFAUT OPTIMISÉS RASPBERRY PI
   population_size=300, generations=800 (via config.py)
"""
import logging
import random

from horizons_core.dataclass.benevole import Benevole
from horizons_core.dataclass.poste import Poste
from typing import Callable

from horizons_core.utils.enums import RecruitmentType
from horizons_genetic.genetic.core.chromosome import Chromosome, LightweightChromosome
from horizons_genetic.genetic.core.population import LightweightPopulation
from horizons_genetic.genetic.fitness.incremental_fitness_calculator import IncrementalFitnessCalculator
from horizons_genetic.genetic.fitness.max_fitness import FitnessMaxCalculator, format_fitness_percentage
from horizons_genetic.genetic.fitness.affectation_scorer import ScoreCache
from horizons_genetic.genetic.operators.crossover.volunteer_crossover import VolunteerCrossover
from horizons_genetic.genetic.operators.initializer import PopulationInitializer
from horizons_genetic.genetic.operators.mutation.adaptative_mutation import AdaptiveMutation
from horizons_genetic.genetic.settings.config import GeneticConfig
from horizons_genetic.genetic.fitness.fitness_weights import GradualFitnessWeights
from horizons_genetic.genetic.utils.chromosome_converter import ChromosomeConverter
from horizons_genetic.genetic.utils.index_manager import IndexManager
from horizons_genetic.genetic.hill_climber import HillClimber

logger = logging.getLogger(__name__)

# Toutes les N générations de stagnation → injection de diversité
_STAGNATION_IMMIGRATION_TRIGGER = 15
# Proportion de la population remplacée par immigration
_IMMIGRATION_RATE = 0.12


class GeneticEngine:
    """
    Orchestre l'algorithme génétique complet.

    Workflow :
      Phase 1 — Initialisation de la population (hybride greedy/random)
      Phase 2 — Évolution sur N générations
                  • Élitisme
                  • Crossover par bénévole (VolunteerCrossover)
                  • Mutations adaptatives
                  • Sélection compétitive
                  • Immigration si stagnation prolongée
      Phase 3 — Hill-climbing sur le meilleur individu
      Phase 4 — Conversion heavy (objets domaine)
    """

    def __init__(
        self,
        config:    GeneticConfig,
        postes:    list[Poste],
        benevoles: list[Benevole],
        on_progress = None
    ):
        self.config    = config
        self.postes    = [p for p in postes if p.get_type() == RecruitmentType.NORMAL]
        self.benevoles = benevoles
        self.on_progress: Callable[..., None] | None = on_progress

        self.index_manager = IndexManager()
        self.index_manager.build_indices(self.postes, benevoles)
        self.all_benevole_ids = set(self.index_manager.get_all_benevole_ids())

        weights = config.fitness_weights or GradualFitnessWeights()

        # ── Cache de scores : construit UNE SEULE FOIS, partagé par tous ──
        logger.info("Construction du cache de scores bénévole × poste…")
        self.score_cache = ScoreCache(self.index_manager)
        logger.info(
            f"Cache de scores construit : "
            f"{len(self.index_manager.get_all_benevole_ids())} bénévoles × "
            f"{len(self.index_manager.get_all_poste_ids())} postes"
        )

        self.fitness_calculator = IncrementalFitnessCalculator(weights, self.index_manager)
        self.initializer        = PopulationInitializer(
            self.postes, benevoles, self.index_manager, score_cache=self.score_cache
        )
        self.crossover          = VolunteerCrossover(
            self.index_manager, score_cache=self.score_cache
        )
        self.mutation           = AdaptiveMutation(
            self.postes,
            self.index_manager,
            config.mutation_rate,
            all_benevole_ids=self.all_benevole_ids,
            score_cache=self.score_cache,
        )
        self.converter          = ChromosomeConverter(self.index_manager)
        self.hill_climber       = HillClimber(
            fitness_calculator=self.fitness_calculator,
            index_manager=self.index_manager,
            all_benevole_ids=self.all_benevole_ids,
            score_cache=self.score_cache,
        )

        self.fitness_max_info = FitnessMaxCalculator(weights).calculate(self.postes, benevoles)
        logger.info(f"Fitness maximum théorique : {self.fitness_max_info.max_total:,.0f}")

    # ------------------------------------------------------------------
    # Point d'entrée public
    # ------------------------------------------------------------------

    def run(self) -> Chromosome:
        # ── Phase 1 : Initialisation ──────────────────────────────────
        logger.info("Phase 1 : Initialisation de la population")
        population = self.initializer.initialize(self.config.population_size)

        filled_counts = [
            sum(1 for b in chrom.poste_to_benevoles.values() for bv in b if bv >= 0)
            for chrom in population
        ]
        logger.info(f"[INIT] Min postes remplis : {min(filled_counts)}")
        logger.info(f"[INIT] Max postes remplis : {max(filled_counts)}")
        logger.info(f"[INIT] Moyenne postes remplis : {sum(filled_counts)/len(filled_counts):.1f}")

        self._evaluate_population(population)

        best_ever        = population.get_best(1)[0]
        stagnation_count = 0

        logger.info(f"Fitness initial (meilleur) : {self._format_fitness(best_ever)}")
        logger.info(
            f"Phase 2 : Évolution sur {self.config.generations} générations "
            f"(crossover_rate={self.config.crossover_rate:.0%})"
        )

        # ── Phase 2 : Évolution ───────────────────────────────────────
        for generation in range(1, self.config.generations + 1):

            population = self._evolve(population)

            current_best    = population.get_best(1)[0]
            current_fitness = current_best.get_fitness()
            best_fitness    = best_ever.get_fitness()

            is_better = (
                current_fitness is not None
                and (best_fitness is None or current_fitness > best_fitness)
            )

            if is_better:
                best_ever        = current_best
                stagnation_count = 0
            else:
                stagnation_count += 1

            # Immigration : diversité forcée en cas de stagnation
            if (
                stagnation_count > 0
                and stagnation_count % _STAGNATION_IMMIGRATION_TRIGGER == 0
            ):
                population = self._immigrate(population)
                logger.info(
                    f"[Immigration] Génération {generation} — "
                    f"injection de {int(self.config.population_size * _IMMIGRATION_RATE)} "
                    f"nouveaux individus après {stagnation_count} générations de stagnation"
                )

            if self.on_progress:
                pct      = int(generation / self.config.generations * 100)
                filled   = current_best.count_filled_positions()
                total    = current_best.count_total_positions()
                assigned = len(current_best.get_assigned_benevoles())
                self.on_progress(
                    pct,
                    f"Génération {generation}/{self.config.generations}",
                    extra={
                        "postes_pourvus":     int(filled),
                        "postes_total":       int(total),
                        "benevoles_affectes": int(assigned),
                        "benevoles_total":    int(len(self.all_benevole_ids)),
                        "satisfaction":       float(self._fitness_pct(current_best)),
                    }
                )

            self._log_generation(generation, current_best, stagnation_count)

            if stagnation_count >= self.config.stagnation_limit:
                logger.info(
                    f"Arrêt anticipé : stagnation depuis {stagnation_count} générations"
                )
                break

        # ── Phase 3 : Hill-climbing ───────────────────────────────────
        logger.info("Phase 3 : Affinage par hill-climbing…")
        best_ever = self.hill_climber.climb(best_ever)
        logger.info(
            f"Fitness après hill-climbing : {self._format_fitness(best_ever)}"
        )

        # ── Phase 4 : Conversion ──────────────────────────────────────
        logger.info("Phase 4 : Conversion de la solution finale")
        return self.converter.to_heavy(best_ever)

    # ------------------------------------------------------------------
    # Évolution
    # ------------------------------------------------------------------

    def _evolve(self, population: LightweightPopulation) -> LightweightPopulation:
        """
        Produit une nouvelle génération.

        TOUS les candidats (élites + enfants + non-parents) concourent
        ensemble pour la sélection. Pression de sélection maximale.

        OPTIMISATION : store_raw=False sur tous les enfants — les raw_scores
        ne sont pas nécessaires pendant l'évolution, seul le scalaire fitness
        guide la sélection.
        """
        population.sort_by_fitness()

        # ── a. Élitisme ───────────────────────────────────────────────
        elite_count = self.config.elite_count
        if not elite_count:
            raise ValueError("elite_count doit être > 0")
        elites = population.get_best(elite_count)

        # ── b. Sélection des parents par tournoi ──────────────────────
        n_parents = max(2, int(population.size() * self.config.crossover_rate))
        if n_parents % 2 != 0:
            n_parents -= 1

        parent_pool = [
            population.tournament_select(self.config.tournament_size)
            for _ in range(n_parents)
        ]
        random.shuffle(parent_pool)

        # ── c. Crossover + Mutation → enfants ─────────────────────────
        children: list[LightweightChromosome] = []
        for i in range(0, len(parent_pool) - 1, 2):
            p1, p2 = parent_pool[i], parent_pool[i + 1]

            child1 = self.crossover.crossover(p1, p2)
            if random.random() < self.config.mutation_rate:
                child1 = self.mutation.mutate(child1)
            # store_raw=False : économie mémoire pendant l'évolution
            self.fitness_calculator.calculate(child1, self.all_benevole_ids, store_raw=False)
            children.append(child1)

            child2 = self.crossover.crossover(p2, p1)
            if random.random() < self.config.mutation_rate:
                child2 = self.mutation.mutate(child2)
            self.fitness_calculator.calculate(child2, self.all_benevole_ids, store_raw=False)
            children.append(child2)

        # ── d. Sélection compétitive ──────────────────────────────────
        all_candidates = list(population)[elite_count:] + children
        candidate_pool = LightweightPopulation(all_candidates)
        candidate_pool.sort_by_fitness()

        slots_remaining = self.config.population_size - elite_count
        survivors       = candidate_pool.get_best(slots_remaining)

        return LightweightPopulation(list(elites) + survivors)

    def _immigrate(self, population: LightweightPopulation) -> LightweightPopulation:
        """
        Remplace les individus les moins performants par de nouveaux chromosomes
        greedy pour réintroduire de la diversité après une stagnation prolongée.
        """
        n_immigrants = max(1, int(self.config.population_size * _IMMIGRATION_RATE))

        immigrants = [
            self.initializer._create_greedy_chromosome()
            for _ in range(n_immigrants)
        ]
        for immigrant in immigrants:
            self.fitness_calculator.calculate(immigrant, self.all_benevole_ids, store_raw=False)

        population.sort_by_fitness()
        chromosomes = list(population)
        chromosomes[-n_immigrants:] = immigrants

        return LightweightPopulation(chromosomes)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _evaluate_population(self, population: LightweightPopulation) -> None:
        for chromosome in population:
            if chromosome.get_fitness() is None:
                # store_raw=False pendant l'initialisation aussi
                self.fitness_calculator.calculate(
                    chromosome, self.all_benevole_ids, store_raw=False
                )

    def _format_fitness(self, chromosome: LightweightChromosome) -> str:
        fitness = chromosome.get_fitness()
        if fitness is None:
            return "non évalué"
        return format_fitness_percentage(fitness, self.fitness_max_info)

    def _fitness_pct(self, chromosome) -> float:
        fitness = chromosome.get_fitness()
        if fitness is None or self.fitness_max_info.max_total == 0:
            return 0.0
        return round(fitness / self.fitness_max_info.max_total * 100, 1)

    def _log_generation(
        self,
        generation: int,
        best:       LightweightChromosome,
        stagnation: int,
    ) -> None:
        filled   = best.count_filled_positions()
        total    = best.count_total_positions()
        pct_fill = filled / total * 100 if total > 0 else 0

        logger.info(
            f"Génération {generation:4d} | "
            f"Fitness={self._format_fitness(best)} | "
            f"Postes={filled}/{total} ({pct_fill:.1f}%) | "
            f"Bénévoles={len(best.get_assigned_benevoles())}/{len(self.all_benevole_ids)} | "
            f"Stag={stagnation}"
        )