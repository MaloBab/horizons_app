"""
Recherche locale par hill-climbing post-génétique.

RÔLE :
  L'algorithme génétique converge vers un bon voisinage de l'espace de
  solutions, mais s'arrête rarement exactement sur un optimum local.
  Ce module affine la meilleure solution trouvée par le GA en tentant
  des améliorations individuelles jusqu'à stagnation complète.

ALGORITHME — Hill-Climbing par perturbations unitaires :

  Tant qu'une amélioration est possible :
    Pour chaque type de perturbation (swap, fill, shift, preference) :
      Générer un candidat voisin via la perturbation
      Si fitness(candidat) > fitness(courant) :
        courant ← candidat
        amélioration trouvée → recommencer depuis le début

  La recherche s'arrête quand aucune des perturbations ne produit
  d'amélioration lors d'un passage complet sur toutes les stratégies.

PARAMÈTRES :
  max_iterations : nombre maximum de passes (garde-fou)
  attempts_per_move : combien de candidats tenter par type de perturbation
                      avant de conclure qu'il n'y a pas d'amélioration

MÉMOIRE :
  On travaille sur un seul chromosome léger à la fois — impact mémoire
  négligeable, aucune copie de population.

INTÉGRATION :
  Appelé par GeneticEngine.run() après la boucle évolutive principale,
  sur best_ever avant la conversion heavy.
"""
import logging
import random

from horizons_genetic.genetic.core.chromosome import LightweightChromosome
from horizons_genetic.genetic.fitness.incremental_fitness_calculator import (
    IncrementalFitnessCalculator,
)
from horizons_genetic.genetic.fitness.affectation_scorer import ScoreCache
from horizons_genetic.genetic.utils.index_manager import IndexManager
from horizons_genetic.genetic.utils.daily_hours_checker import (
    compute_daily_hours,
    violates_daily_limit,
)

logger = logging.getLogger(__name__)


class HillClimber:
    """
    Affine un chromosome par perturbations unitaires successives.

    Chaque perturbation est évaluée par le calculateur de fitness complet.
    La recherche s'arrête quand plus aucune amélioration n'est trouvée.
    """

    def __init__(
        self,
        fitness_calculator: IncrementalFitnessCalculator,
        index_manager:      IndexManager,
        all_benevole_ids:   set[int],
        score_cache:        ScoreCache,
        max_iterations:     int = 200,
        attempts_per_move:  int = 15,
    ):
        self.fitness_calculator = fitness_calculator
        self.index_manager      = index_manager
        self.all_benevole_ids   = all_benevole_ids
        self.score_cache        = score_cache
        self.max_iterations     = max_iterations
        self.attempts_per_move  = attempts_per_move

    # ------------------------------------------------------------------
    # Point d'entrée public
    # ------------------------------------------------------------------

    def climb(self, chromosome: LightweightChromosome) -> LightweightChromosome:
        """
        Affine le chromosome par hill-climbing.

        Args:
            chromosome: Meilleur individu issu du GA (doit avoir un fitness calculé).

        Returns:
            Chromosome amélioré (ou identique si déjà à l'optimum local).
        """
        current       = chromosome
        current_fit   = current.get_fitness() or 0.0
        initial_fit   = current_fit
        n_improvements = 0
        iteration = -1

        for iteration in range(self.max_iterations):
            improved = False

            # Essayer chaque stratégie de perturbation
            for move_fn in [
                self._try_swap,
                self._try_fill,
                self._try_shift,
                self._try_preference_swap,
            ]:
                candidate = move_fn(current)
                if candidate is current:
                    continue  # perturbation n'a rien produit

                # Évaluer le candidat (sans stocker les raw_scores)
                cand_fit = self.fitness_calculator.calculate(
                    candidate, self.all_benevole_ids, store_raw=False
                )

                if cand_fit > current_fit:
                    current     = candidate
                    current_fit = cand_fit
                    improved    = True
                    n_improvements += 1
                    # Recommencer immédiatement avec le nouveau courant
                    break

            if not improved:
                # Aucune perturbation n'a amélioré le fitness → optimum local atteint
                break

        gain = current_fit - initial_fit
        logger.info(
            f"[HillClimbing] {n_improvements} amélioration(s) en {iteration + 1} itération(s) "
            f"| Gain fitness : {gain:+.1f}"
        )

        # Stocker les raw_scores sur le meilleur individu final
        self.fitness_calculator.calculate(current, self.all_benevole_ids, store_raw=True)

        return current

    # ------------------------------------------------------------------
    # Perturbations unitaires
    # ------------------------------------------------------------------

    def _try_swap(self, chromosome: LightweightChromosome) -> LightweightChromosome:
        """
        Tente un échange de deux bénévoles entre deux postes.
        Retourne le chromosome original si aucun swap valide n'est trouvé.
        """
        all_ids = list(chromosome.poste_to_benevoles.keys())
        if len(all_ids) < 2:
            return chromosome

        daily_hours = compute_daily_hours(chromosome.poste_to_benevoles, self.index_manager)
        assignments = chromosome.get_benevole_assignments()

        for _ in range(self.attempts_per_move):
            p1_id = random.choice(all_ids)
            p2_id = random.choice([p for p in all_ids if p != p1_id])

            bvs1  = chromosome.poste_to_benevoles[p1_id]
            bvs2  = chromosome.poste_to_benevoles[p2_id]

            valid1 = [b for b in bvs1 if b >= 0]
            if not valid1:
                continue

            b1_id = random.choice(valid1)
            idx1  = bvs1.index(b1_id)
            idx2  = random.randint(0, len(bvs2) - 1)
            b2_id = bvs2[idx2]

            if self._swap_valid(chromosome, b1_id, p1_id, b2_id, p2_id, daily_hours, assignments):
                mutated = chromosome.clone()
                mutated.poste_to_benevoles[p1_id][idx1] = b2_id
                mutated.poste_to_benevoles[p2_id][idx2] = b1_id
                return mutated

        return chromosome

    def _try_fill(self, chromosome: LightweightChromosome) -> LightweightChromosome:
        """
        Tente de combler un slot vide avec le meilleur bénévole disponible.
        """
        empty_slots = [
            (p_id, i)
            for p_id, bvs in chromosome.poste_to_benevoles.items()
            for i, b in enumerate(bvs)
            if b < 0
        ]
        if not empty_slots:
            return chromosome

        daily_hours = compute_daily_hours(chromosome.poste_to_benevoles, self.index_manager)
        assignments = chromosome.get_benevole_assignments()
        all_b_ids   = list(self.all_benevole_ids)

        # Choisir le slot vide avec le meilleur candidat potentiel
        random.shuffle(empty_slots)
        sample = empty_slots[:self.attempts_per_move]

        for poste_id, slot in sample:
            # Trier les bénévoles par score (via cache)
            candidates = sorted(
                all_b_ids,
                key=lambda b: self.score_cache.get(b, poste_id),
                reverse=True,
            )

            for b_id in candidates[:self.attempts_per_move]:
                if b_id in chromosome.poste_to_benevoles.get(poste_id, []):
                    continue
                benevole = self.index_manager.id_to_benevole(b_id)
                poste    = self.index_manager.id_to_poste(poste_id)
                if benevole is None or poste is None:
                    continue
                creneau = poste.get_horaire()
                if not benevole.is_disponible(creneau):
                    continue
                # Vérifier les conflits horaires
                conflict = any(
                    creneau.is_incompatible(self.index_manager.id_to_poste(op).get_horaire())
                    for op in assignments.get(b_id, [])
                )
                if conflict:
                    continue
                if violates_daily_limit(b_id, creneau, daily_hours, self.index_manager):
                    continue

                mutated = chromosome.clone()
                mutated.poste_to_benevoles[poste_id][slot] = b_id
                return mutated

        return chromosome

    def _try_shift(self, chromosome: LightweightChromosome) -> LightweightChromosome:
        """
        Déplace un bénévole vers un poste du même pôle avec un meilleur score.
        Cible les bénévoles mal placés par rapport à leurs préférences.
        """
        all_ids = list(chromosome.poste_to_benevoles.keys())
        daily_hours = compute_daily_hours(chromosome.poste_to_benevoles, self.index_manager)
        assignments = chromosome.get_benevole_assignments()

        for _ in range(self.attempts_per_move):
            p1_id = random.choice(all_ids)
            bvs1  = chromosome.poste_to_benevoles[p1_id]
            valid = [b for b in bvs1 if b >= 0]
            if not valid:
                continue

            b_id   = random.choice(valid)
            idx1   = bvs1.index(b_id)
            score1 = self.score_cache.get(b_id, p1_id)

            # Chercher un poste qui serait mieux pour ce bénévole
            better = [
                p2_id for p2_id in all_ids
                if p2_id != p1_id
                and self.score_cache.get(b_id, p2_id) > score1
            ]
            if not better:
                continue

            p2_id  = random.choice(better)
            bvs2   = chromosome.poste_to_benevoles[p2_id]
            idx2   = random.randint(0, len(bvs2) - 1)
            b2_id  = bvs2[idx2]

            if self._swap_valid(chromosome, b_id, p1_id, b2_id, p2_id, daily_hours, assignments):
                mutated = chromosome.clone()
                mutated.poste_to_benevoles[p1_id][idx1] = b2_id
                mutated.poste_to_benevoles[p2_id][idx2] = b_id
                return mutated

        return chromosome

    def _try_preference_swap(self, chromosome: LightweightChromosome) -> LightweightChromosome:
        """
        Échange deux bénévoles dans la même catégorie de pôle pour améliorer
        l'adéquation préférences ↔ poste.
        """
        all_ids = list(chromosome.poste_to_benevoles.keys())
        daily_hours = compute_daily_hours(chromosome.poste_to_benevoles, self.index_manager)
        assignments = chromosome.get_benevole_assignments()

        # Regrouper les postes par pôle
        by_pole: dict[int, list[int]] = {}
        for p_id in all_ids:
            poste = self.index_manager.id_to_poste(p_id)
            if poste:
                pole = poste.get_categorie().pole_id
                by_pole.setdefault(pole, []).append(p_id)

        eligible_poles = [k for k, v in by_pole.items() if len(v) >= 2]
        if not eligible_poles:
            return chromosome

        for _ in range(self.attempts_per_move):
            pole_id  = random.choice(eligible_poles)
            p1_id, p2_id = random.sample(by_pole[pole_id], 2)

            bvs1 = chromosome.poste_to_benevoles[p1_id]
            bvs2 = chromosome.poste_to_benevoles[p2_id]
            if not bvs1 or not bvs2:
                continue

            idx1  = random.randint(0, len(bvs1) - 1)
            idx2  = random.randint(0, len(bvs2) - 1)
            b1_id = bvs1[idx1]
            b2_id = bvs2[idx2]

            if self._swap_valid(chromosome, b1_id, p1_id, b2_id, p2_id, daily_hours, assignments):
                mutated = chromosome.clone()
                mutated.poste_to_benevoles[p1_id][idx1] = b2_id
                mutated.poste_to_benevoles[p2_id][idx2] = b1_id
                return mutated

        return chromosome

    # ------------------------------------------------------------------
    # Validation interne
    # ------------------------------------------------------------------

    def _swap_valid(
        self,
        chromosome:  LightweightChromosome,
        b1_id:       int,
        poste1_id:   int,
        b2_id:       int,
        poste2_id:   int,
        daily_hours: dict[int, dict[int, float]],
        assignments: dict[int, list[int]],
    ) -> bool:
        """Vérifie que l'échange (b1 ↔ b2) entre poste1 et poste2 est valide."""
        p1 = self.index_manager.id_to_poste(poste1_id)
        p2 = self.index_manager.id_to_poste(poste2_id)
        if p1 is None or p2 is None:
            return False
        c1 = p1.get_horaire()
        c2 = p2.get_horaire()

        def _ok(b_id: int, old_pid: int, new_c) -> bool:
            if b_id < 0:
                return True
            bv = self.index_manager.id_to_benevole(b_id)
            if bv is None or not bv.is_disponible(new_c):
                return False
            for other_pid in assignments.get(b_id, []):
                if other_pid == old_pid:
                    continue
                if new_c.is_incompatible(
                    self.index_manager.id_to_poste(other_pid).get_horaire()
                ):
                    return False
            old_c = self.index_manager.id_to_poste(old_pid).get_horaire()
            sim   = {d: h for d, h in daily_hours.get(b_id, {}).items()}
            oj    = old_c.get_jour()
            sim[oj] = sim.get(oj, 0.0) - (old_c.get_borne_sup() - old_c.get_borne_inf())
            return not violates_daily_limit(b_id, new_c, {b_id: sim}, self.index_manager)

        return _ok(b1_id, poste1_id, c2) and _ok(b2_id, poste2_id, c1)