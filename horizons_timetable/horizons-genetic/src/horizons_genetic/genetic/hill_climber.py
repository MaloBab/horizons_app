"""
Recherche locale par hill-climbing post-génétique — v2.
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
    Affine un chromosome par perturbations unitaires guidées et exhaustives.
    Ne s'arrête qu'après max_no_improve passes consécutives sans amélioration.
    """

    def __init__(
        self,
        fitness_calculator: IncrementalFitnessCalculator,
        index_manager:      IndexManager,
        all_benevole_ids:   set[int],
        score_cache:        ScoreCache,
        max_iterations:     int = 200,    # garde-fou absolu
        attempts_per_move:  int = 50,     # v2 : 50 au lieu de 15
        max_no_improve:     int = 5,      # v2 : 5 passes sans amélioration → arrêt
        restart_every:      int = 3,      # v2 : perturbation forte tous les N échecs
    ):
        self.fitness_calculator = fitness_calculator
        self.index_manager      = index_manager
        self.all_benevole_ids   = all_benevole_ids
        self.score_cache        = score_cache
        self.max_iterations     = max_iterations
        self.attempts_per_move  = attempts_per_move
        self.max_no_improve     = max_no_improve
        self.restart_every      = restart_every

        # Pré-calcul des index de disponibilité (partagé avec AdaptiveMutation)
        self._eligible_postes:    dict[int, list[int]] = {}
        self._eligible_benevoles: dict[int, list[int]] = {}
        self._build_eligibility()

    def _build_eligibility(self) -> None:
        all_b_ids = list(self.all_benevole_ids)
        all_p_ids = self.index_manager.get_all_poste_ids()

        for b_id in all_b_ids:
            bv = self.index_manager.id_to_benevole(b_id)
            if bv is None:
                self._eligible_postes[b_id] = []
                continue
            self._eligible_postes[b_id] = [
                p_id for p_id in all_p_ids
                if self.index_manager.id_to_poste(p_id) is not None
                and bv.is_disponible(self.index_manager.id_to_poste(p_id).get_horaire())
            ]

        for p_id in all_p_ids:
            p = self.index_manager.id_to_poste(p_id)
            if p is None:
                self._eligible_benevoles[p_id] = []
                continue
            c = p.get_horaire()
            self._eligible_benevoles[p_id] = [
                b_id for b_id in all_b_ids
                if (benev:= self.index_manager.id_to_benevole(b_id)) is not None
                and benev.is_disponible(c)
            ]

    # ------------------------------------------------------------------
    # Point d'entrée public
    # ------------------------------------------------------------------

    def climb(self, chromosome: LightweightChromosome) -> LightweightChromosome:
        """
        Affine le chromosome par hill-climbing multi-passes.

        Returns:
            Le meilleur chromosome trouvé (≥ chromosome initial).
        """
        current       = chromosome
        current_fit   = current.get_fitness() or 0.0
        initial_fit   = current_fit
        n_improvements = 0
        no_improve_streak = 0
        iteration     = 0

        for iteration in range(self.max_iterations):
            improved = False

            for move_fn in [
                self._try_swap,
                self._try_fill,
                self._try_shift,
                self._try_preference_swap,
            ]:
                for _ in range(self.attempts_per_move):
                    candidate = move_fn(current)
                    if candidate is current:
                        continue

                    cand_fit = self.fitness_calculator.calculate(
                        candidate, self.all_benevole_ids, store_raw=False
                    )

                    if cand_fit > current_fit:
                        current       = candidate
                        current_fit   = cand_fit
                        improved      = True
                        n_improvements += 1
                        break  # Redémarrer depuis swap avec le nouvel état

                if improved:
                    break   # Recommencer la passe depuis le début

            if improved:
                no_improve_streak = 0
            else:
                no_improve_streak += 1

                # Restart aléatoire pour sortir des bassins locaux
                if no_improve_streak % self.restart_every == 0 and no_improve_streak > 0:
                    perturbed     = self._random_perturbation(current)
                    perturbed_fit = self.fitness_calculator.calculate(
                        perturbed, self.all_benevole_ids, store_raw=False
                    )
                    if perturbed_fit > current_fit:
                        current     = perturbed
                        current_fit = perturbed_fit
                        n_improvements += 1
                        no_improve_streak = 0
                    # Sinon on garde current (best_ever maintenu implicitement)

                if no_improve_streak >= self.max_no_improve:
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
    # Perturbations
    # ------------------------------------------------------------------

    def _try_swap(self, chromosome: LightweightChromosome) -> LightweightChromosome:
        """Swap guidé par l'index d'éligibilité."""
        all_ids = list(chromosome.poste_to_benevoles.keys())
        if len(all_ids) < 2:
            return chromosome

        daily_hours = compute_daily_hours(chromosome.poste_to_benevoles, self.index_manager)
        assignments = chromosome.get_benevole_assignments()

        # Tirer un poste source non vide
        occupied = [p for p in all_ids if any(b >= 0 for b in chromosome.poste_to_benevoles[p])]
        if not occupied:
            return chromosome

        p1_id = random.choice(occupied)
        bvs1  = chromosome.poste_to_benevoles[p1_id]
        valid = [b for b in bvs1 if b >= 0]
        if not valid:
            return chromosome

        b1_id = random.choice(valid)
        idx1  = bvs1.index(b1_id)

        # Postes candidats pour p2 : b1 doit être disponible (index statique)
        b1_elig = set(self._eligible_postes.get(b1_id, []))
        elig_p1_bvs = set(self._eligible_benevoles.get(p1_id, []))

        candidates_p2 = [
            p_id for p_id in all_ids
            if p_id != p1_id
            and p_id in b1_elig
        ]

        if not candidates_p2:
            return chromosome

        random.shuffle(candidates_p2)
        for p2_id in candidates_p2[:self.attempts_per_move]:
            bvs2 = chromosome.poste_to_benevoles[p2_id]
            idx2 = random.randint(0, len(bvs2) - 1)
            b2_id = bvs2[idx2]

            if self._swap_valid(chromosome, b1_id, p1_id, b2_id, p2_id, daily_hours, assignments):
                mutated = chromosome.clone()
                mutated.poste_to_benevoles[p1_id][idx1] = b2_id
                mutated.poste_to_benevoles[p2_id][idx2] = b1_id
                return mutated

        return chromosome

    def _try_fill(self, chromosome: LightweightChromosome) -> LightweightChromosome:
        """Fill guidé : trie les candidats par score dans l'index d'éligibilité."""
        empty_slots = [
            (p_id, i)
            for p_id, bvs in chromosome.poste_to_benevoles.items()
            for i, b in enumerate(bvs) if b < 0
        ]
        if not empty_slots:
            return chromosome

        daily_hours = compute_daily_hours(chromosome.poste_to_benevoles, self.index_manager)
        assignments = chromosome.get_benevole_assignments()

        random.shuffle(empty_slots)
        sample = empty_slots[:self.attempts_per_move]

        for poste_id, slot in sample:
            candidates = sorted(
                self._eligible_benevoles.get(poste_id, []),
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
        """Déplace un bénévole vers un poste avec un meilleur score."""
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

            # Chercher dans l'index d'éligibilité les postes avec meilleur score
            b_elig = self._eligible_postes.get(b_id, [])
            better = [p for p in b_elig if p != p1_id and self.score_cache.get(b_id, p) > score1]
            if not better:
                continue

            p2_id  = random.choice(better)
            bvs2   = chromosome.poste_to_benevoles.get(p2_id, [])
            if not bvs2:
                continue

            idx2  = random.randint(0, len(bvs2) - 1)
            b2_id = bvs2[idx2]

            if self._swap_valid(chromosome, b_id, p1_id, b2_id, p2_id, daily_hours, assignments):
                mutated = chromosome.clone()
                mutated.poste_to_benevoles[p1_id][idx1] = b2_id
                mutated.poste_to_benevoles[p2_id][idx2] = b_id
                return mutated

        return chromosome

    def _try_preference_swap(self, chromosome: LightweightChromosome) -> LightweightChromosome:
        """Swap dans la même catégorie pour améliorer les préférences."""
        all_ids = list(chromosome.poste_to_benevoles.keys())
        daily_hours = compute_daily_hours(chromosome.poste_to_benevoles, self.index_manager)
        assignments = chromosome.get_benevole_assignments()

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
            pole_id   = random.choice(eligible_poles)
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

    def _random_perturbation(self, chromosome: LightweightChromosome) -> LightweightChromosome:
        """
        Perturbation forte aléatoire (3 swaps successifs) pour sortir d'un bassin local.
        Utilisée lors des restarts.
        """
        mutated = chromosome.clone()
        all_ids = list(mutated.poste_to_benevoles.keys())

        for _ in range(3):
            if len(all_ids) < 2:
                break
            p1_id, p2_id = random.sample(all_ids, 2)
            bvs1 = mutated.poste_to_benevoles[p1_id]
            bvs2 = mutated.poste_to_benevoles[p2_id]
            if not bvs1 or not bvs2:
                continue
            idx1 = random.randint(0, len(bvs1) - 1)
            idx2 = random.randint(0, len(bvs2) - 1)

            daily_hours = compute_daily_hours(mutated.poste_to_benevoles, self.index_manager)
            assignments = mutated.get_benevole_assignments()

            if self._swap_valid(mutated, bvs1[idx1], p1_id, bvs2[idx2], p2_id, daily_hours, assignments):
                b1_id = bvs1[idx1]
                b2_id = bvs2[idx2]
                mutated.poste_to_benevoles[p1_id][idx1] = b2_id
                mutated.poste_to_benevoles[p2_id][idx2] = b1_id

        return mutated

    # ------------------------------------------------------------------
    # Validation
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
                if new_c.is_incompatible(self.index_manager.id_to_poste(other_pid).get_horaire()):
                    return False
            old_c = self.index_manager.id_to_poste(old_pid).get_horaire()
            sim   = {d: h for d, h in daily_hours.get(b_id, {}).items()}
            oj    = old_c.get_jour()
            sim[oj] = sim.get(oj, 0.0) - (old_c.get_borne_sup() - old_c.get_borne_inf())
            return not violates_daily_limit(b_id, new_c, {b_id: sim}, self.index_manager)

        return _ok(b1_id, poste1_id, c2) and _ok(b2_id, poste2_id, c1)