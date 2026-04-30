"""
Mutations adaptatives avec garantie de validité (contraintes dures).

Types de mutation :
  - Fill       (35 %) : ajoute un bénévole déjà affecté à un slot vide supplémentaire
  - Swap       (30 %) : échange deux bénévoles entre deux postes
  - Inject     (15 %) : place un bénévole non affecté dans un slot vide (si surplus)
  - Shift      (10 %) : déplace un bénévole vers un poste temporellement adjacent
  - Preference (10 %) : swap dans la même catégorie pour améliorer les préférences

OPTIMISATION — ScoreCache :
  Les appels répétés à score_affectation() dans _fill_mutation représentaient
  le principal goulot d'étranglement CPU (tri de tous les bénévoles pour chaque
  slot vide, à chaque mutation). On utilise maintenant ScoreCache.get() — O(1)
  au lieu de recalculer disponibilité + préférences à chaque fois.
"""
import random
from typing import Callable

from horizons_core.dataclass.poste import Poste
from horizons_genetic.genetic.core.chromosome import LightweightChromosome
from horizons_genetic.genetic.operators.mutation.i_mutation import MutationOperator
from horizons_genetic.genetic.fitness.affectation_scorer import ScoreCache
from horizons_genetic.genetic.utils.index_manager import IndexManager
from horizons_genetic.genetic.utils.daily_hours_checker import (
    compute_daily_hours,
    violates_daily_limit,
)


class AdaptiveMutation(MutationOperator):
    """
    Applique plusieurs mutations successives en respectant les contraintes dures.

    Chaque mutation est validée avant d'être appliquée :
      - Disponibilité du bénévole sur le créneau
      - Pas de conflit horaire avec ses autres affectations
      - Limite journalière respectée (NORMAL 6h, SPÉCIALISÉ 2h)
    """

    def __init__(
        self,
        postes:             list[Poste],
        index_manager:      IndexManager,
        base_mutation_rate: float = 0.06,
        max_retries:        int   = 10,
        all_benevole_ids:   set[int] | None = None,
        score_cache:        ScoreCache | None = None,
    ):
        self.postes             = postes
        self.index_manager      = index_manager
        self.base_mutation_rate = base_mutation_rate
        self.max_retries        = max_retries
        self.all_benevole_ids   = all_benevole_ids or set()

        # ── Cache de scores statique ──────────────────────────────────
        # Construit une seule fois, partagé avec GeneticEngine et
        # PopulationInitializer pour éviter plusieurs allocations.
        self.score_cache = score_cache or ScoreCache(index_manager)

        self.benevoles = [
            index_manager.id_to_benevole(i)
            for i in range(len(index_manager._id_to_benevole))
        ]

        # (fonction, probabilité) — somme = 1.0
        self.mutation_types: list[tuple[Callable, float]] = [
            (self._fill_mutation,       0.35),
            (self._swap_mutation,       0.30),
            (self._inject_mutation,     0.15),
            (self._shift_mutation,      0.10),
            (self._preference_mutation, 0.10),
        ]

        self.adjacent_postes:    dict[int, list[int]] = {}
        self.postes_by_category: dict[int, list[int]] = {}
        self._build_structures()

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _build_structures(self) -> None:
        for p1 in self.postes:
            p1_id = self.index_manager.poste_to_id(p1)
            c1    = p1.get_horaire()
            self.adjacent_postes[p1_id] = [
                self.index_manager.poste_to_id(p2)
                for p2 in self.postes
                if p2 != p1
                and c1.get_jour() == p2.get_horaire().get_jour()
                and (
                    c1.get_borne_sup() == p2.get_horaire().get_borne_inf()
                    or p2.get_horaire().get_borne_sup() == c1.get_borne_inf()
                )
            ]

        for p in self.postes:
            pole_id = p.get_categorie().pole_id
            self.postes_by_category.setdefault(pole_id, []).append(
                self.index_manager.poste_to_id(p)
            )

    # ------------------------------------------------------------------
    # Point d'entrée public
    # ------------------------------------------------------------------

    def mutate(self, chromosome: LightweightChromosome) -> LightweightChromosome:
        """
        Applique 2 à 4 mutations successives.
        Les 2 premières sont toujours exécutées.
        Les suivantes ont une probabilité décroissante (0.6 par étape).
        """
        mutated     = chromosome
        n_mutations = random.randint(2, 4)
        for i in range(n_mutations):
            if i >= 2 and random.random() > 0.6:
                break
            mutation_fn = self._select_mutation_type()
            mutated     = mutation_fn(mutated)
        return mutated

    # ------------------------------------------------------------------
    # Sélection du type de mutation
    # ------------------------------------------------------------------

    def _select_mutation_type(self) -> Callable:
        rand       = random.random()
        cumulative = 0.0
        for fn, prob in self.mutation_types:
            cumulative += prob
            if rand < cumulative:
                return fn
        return self.mutation_types[0][0]

    # ------------------------------------------------------------------
    # Validation commune
    # ------------------------------------------------------------------

    def _is_assignable(
        self,
        b_id:        int,
        poste_id:    int,
        daily_hours: dict[int, dict[int, float]],
        assignments: dict[int, list[int]],
    ) -> bool:
        """
        Vérifie qu'affecter b_id au poste poste_id est valide :
          - bénévole disponible sur ce créneau
          - pas de conflit horaire avec ses affectations actuelles
          - limite journalière respectée
        """
        benevole = self.index_manager.id_to_benevole(b_id)
        poste    = self.index_manager.id_to_poste(poste_id)
        if benevole is None or poste is None:
            return False

        creneau = poste.get_horaire()

        if not benevole.is_disponible(creneau):
            return False

        for other_poste_id in assignments.get(b_id, []):
            other_c = self.index_manager.id_to_poste(other_poste_id).get_horaire()
            if creneau.is_incompatible(other_c):
                return False

        if violates_daily_limit(b_id, creneau, daily_hours, self.index_manager):
            return False

        return True

    def _is_swap_valid(
        self,
        chromosome: LightweightChromosome,
        b1_id:      int,
        poste1_id:  int,
        b2_id:      int,
        poste2_id:  int,
    ) -> bool:
        poste1   = self.index_manager.id_to_poste(poste1_id)
        poste2   = self.index_manager.id_to_poste(poste2_id)
        creneau1 = poste1.get_horaire()
        creneau2 = poste2.get_horaire()

        assignments = chromosome.get_benevole_assignments()
        daily_hours = compute_daily_hours(chromosome.poste_to_benevoles, self.index_manager)

        def _check(b_id, old_poste_id, new_creneau) -> bool:
            if b_id < 0:
                return True
            benevole = self.index_manager.id_to_benevole(b_id)
            if benevole is None or not benevole.is_disponible(new_creneau):
                return False
            for other_id in assignments.get(b_id, []):
                if other_id == old_poste_id:
                    continue
                if new_creneau.is_incompatible(
                    self.index_manager.id_to_poste(other_id).get_horaire()
                ):
                    return False
            old_c  = self.index_manager.id_to_poste(old_poste_id).get_horaire()
            sim    = {day: h for day, h in daily_hours.get(b_id, {}).items()}
            old_j  = old_c.get_jour()
            sim[old_j] = sim.get(old_j, 0.0) - (old_c.get_borne_sup() - old_c.get_borne_inf())
            if violates_daily_limit(b_id, new_creneau, {b_id: sim}, self.index_manager):
                return False
            return True

        return _check(b1_id, poste1_id, creneau2) and _check(b2_id, poste2_id, creneau1)

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------

    def _fill_mutation(self, chromosome: LightweightChromosome) -> LightweightChromosome:
        """
        Ajoute un bénévole DÉJÀ AFFECTÉ à un slot vide supplémentaire.

        OPTIMISATION : utilise score_cache.get() au lieu de score_affectation()
        pour les tris de candidats — O(1) au lieu de recalculer disponibilité
        et préférences à chaque appel.
        """
        empty_slots = [
            (p_id, i)
            for p_id, benevoles in chromosome.poste_to_benevoles.items()
            for i, b in enumerate(benevoles)
            if b < 0
        ]
        if not empty_slots:
            return chromosome

        # Batch adaptatif selon le taux de remplissage
        total     = chromosome.count_total_positions()
        filled    = chromosome.count_filled_positions()
        fill_rate = filled / total if total > 0 else 0.0

        if fill_rate < 0.70:
            max_fills = 4
        elif fill_rate < 0.85:
            max_fills = 2
        else:
            max_fills = 1

        # Pré-calcul partagé pour tout le batch
        daily_hours = compute_daily_hours(chromosome.poste_to_benevoles, self.index_manager)
        assignments = chromosome.get_benevole_assignments()
        all_b_ids   = list(self.all_benevole_ids)

        # Échantillon de slots vides à traiter
        candidate_slots = random.sample(
            empty_slots, min(len(empty_slots), max_fills * 4)
        )

        # Trier les slots par score du meilleur candidat disponible (via cache)
        scored_slots = sorted(
            candidate_slots,
            key=lambda slot: max(
                (self.score_cache.get(b_id, slot[0]) for b_id in all_b_ids),
                default=0.0,
            ),
            reverse=True,
        )

        mutated  = chromosome.clone()
        n_filled = 0

        for poste_id, slot in scored_slots:
            if n_filled >= max_fills:
                break

            # Trier les candidats par score pour ce poste précis (via cache)
            scored_candidates = sorted(
                all_b_ids,
                key=lambda b_id: self.score_cache.get(b_id, poste_id),
                reverse=True,
            )

            for b_id in scored_candidates[:self.max_retries]:
                if b_id in mutated.poste_to_benevoles.get(poste_id, []):
                    continue

                if self._is_assignable(b_id, poste_id, daily_hours, assignments):
                    mutated.poste_to_benevoles[poste_id][slot] = b_id

                    # Mise à jour incrémentale
                    creneau = self.index_manager.id_to_poste(poste_id).get_horaire()
                    jour    = creneau.get_jour()
                    duree   = creneau.get_borne_sup() - creneau.get_borne_inf()
                    if b_id not in daily_hours:
                        daily_hours[b_id] = {}
                    daily_hours[b_id][jour] = daily_hours[b_id].get(jour, 0.0) + duree
                    assignments.setdefault(b_id, []).append(poste_id)

                    n_filled += 1
                    break

        return mutated if n_filled > 0 else chromosome

    def _inject_mutation(self, chromosome: LightweightChromosome) -> LightweightChromosome:
        """
        Place un bénévole NON AFFECTÉ dans un slot vide.
        Utile uniquement quand il y a un surplus de bénévoles.
        """
        assigned   = chromosome.get_assigned_benevoles()
        unassigned = list(self.all_benevole_ids - assigned)
        if not unassigned:
            return chromosome

        empty_slots = [
            (p_id, i)
            for p_id, benevoles in chromosome.poste_to_benevoles.items()
            for i, b in enumerate(benevoles)
            if b < 0
        ]
        if not empty_slots:
            return chromosome

        daily_hours = compute_daily_hours(chromosome.poste_to_benevoles, self.index_manager)
        assignments = chromosome.get_benevole_assignments()

        random.shuffle(unassigned)
        random.shuffle(empty_slots)

        for b_id in unassigned[:self.max_retries]:
            for poste_id, slot in empty_slots[:self.max_retries]:
                if self._is_assignable(b_id, poste_id, daily_hours, assignments):
                    mutated = chromosome.clone()
                    mutated.poste_to_benevoles[poste_id][slot] = b_id
                    return mutated

        return chromosome

    def _swap_mutation(self, chromosome: LightweightChromosome) -> LightweightChromosome:
        """Échange deux bénévoles entre deux postes quelconques."""
        all_ids = list(chromosome.poste_to_benevoles.keys())
        if len(all_ids) < 2:
            return chromosome

        for _ in range(self.max_retries):
            poste1_id  = random.choice(all_ids)
            benevoles1 = chromosome.poste_to_benevoles[poste1_id]
            valid1     = [b for b in benevoles1 if b >= 0]
            if not valid1:
                continue

            b1_id = random.choice(valid1)
            idx1  = benevoles1.index(b1_id)

            poste2_id  = random.choice([p for p in all_ids if p != poste1_id])
            benevoles2 = chromosome.poste_to_benevoles[poste2_id]
            if not benevoles2:
                continue

            idx2  = random.randint(0, len(benevoles2) - 1)
            b2_id = benevoles2[idx2]

            if self._is_swap_valid(chromosome, b1_id, poste1_id, b2_id, poste2_id):
                mutated = chromosome.clone()
                mutated.poste_to_benevoles[poste1_id][idx1] = b2_id
                mutated.poste_to_benevoles[poste2_id][idx2] = b1_id
                return mutated

        return chromosome

    def _shift_mutation(self, chromosome: LightweightChromosome) -> LightweightChromosome:
        """Déplace un bénévole vers un poste temporellement adjacent."""
        occupied = [
            p_id for p_id in chromosome.poste_to_benevoles
            if any(b >= 0 for b in chromosome.poste_to_benevoles[p_id])
        ]
        if not occupied:
            return chromosome

        for _ in range(self.max_retries):
            poste1_id  = random.choice(occupied)
            adj_ids    = self.adjacent_postes.get(poste1_id, [])
            if not adj_ids:
                continue

            poste2_id  = random.choice(adj_ids)
            benevoles1 = chromosome.poste_to_benevoles[poste1_id]
            benevoles2 = chromosome.poste_to_benevoles[poste2_id]

            valid1 = [b for b in benevoles1 if b >= 0]
            if not valid1 or not benevoles2:
                continue

            b1_id = random.choice(valid1)
            idx1  = benevoles1.index(b1_id)
            idx2  = random.randint(0, len(benevoles2) - 1)
            b2_id = benevoles2[idx2]

            if self._is_swap_valid(chromosome, b1_id, poste1_id, b2_id, poste2_id):
                mutated = chromosome.clone()
                mutated.poste_to_benevoles[poste1_id][idx1] = b2_id
                mutated.poste_to_benevoles[poste2_id][idx2] = b1_id
                return mutated

        return chromosome

    def _preference_mutation(self, chromosome: LightweightChromosome) -> LightweightChromosome:
        """Échange deux bénévoles dans la même catégorie (amélioration des préférences)."""
        eligible = [
            pole_id for pole_id, ids in self.postes_by_category.items()
            if len(ids) >= 2
        ]
        if not eligible:
            return chromosome

        for _ in range(self.max_retries):
            pole_id              = random.choice(eligible)
            poste1_id, poste2_id = random.sample(self.postes_by_category[pole_id], 2)

            benevoles1 = chromosome.poste_to_benevoles[poste1_id]
            benevoles2 = chromosome.poste_to_benevoles[poste2_id]
            if not benevoles1 or not benevoles2:
                continue

            idx1  = random.randint(0, len(benevoles1) - 1)
            idx2  = random.randint(0, len(benevoles2) - 1)
            b1_id = benevoles1[idx1]
            b2_id = benevoles2[idx2]

            if self._is_swap_valid(chromosome, b1_id, poste1_id, b2_id, poste2_id):
                mutated = chromosome.clone()
                mutated.poste_to_benevoles[poste1_id][idx1] = b2_id
                mutated.poste_to_benevoles[poste2_id][idx2] = b1_id
                return mutated

        return chromosome