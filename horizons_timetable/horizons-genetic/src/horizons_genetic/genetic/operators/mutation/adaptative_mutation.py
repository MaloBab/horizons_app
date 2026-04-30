"""
Mutations adaptatives — v2 : valides par construction.

PROBLÈME v1 :
  Chaque mutation reposait sur une boucle "tirer au hasard → tester → retenter"
  (max_retries=10). Avec 140 bénévoles sur 268 postes contraints, la grande
  majorité des tirages échouaient. Résultat : beaucoup de mutations retournaient
  le chromosome original sans aucune modification.

APPROCHE v2 — "valide par construction" :

  1. INDEX D'ÉLIGIBILITÉ STATIQUE (construit une seule fois à l'init)
     Pour chaque paire (bénévole, poste), on pré-calcule si le bénévole est
     disponible sur ce créneau. Cela élimine ~70-80 % des candidates avant même
     de regarder les conflits contextuels.

       eligible_postes[b_id]    = liste des poste_ids où b_id est disponible
       eligible_benevoles[p_id] = liste des b_ids disponibles sur ce poste

  2. SWAP VALIDE PAR CONSTRUCTION (_swap_mutation)
     Au lieu de tirer deux postes aléatoires et tester, on :
       a. Tire un bénévole b1 dans un poste p1
       b. Identifie directement les postes p2 où b1 est disponible ET dont le
          bénévole en place b2 est disponible sur p1 (compatible croisé)
       c. Tire dans cette liste pré-filtrée → le swap est valide par construction
          sous réserve de la vérification des conflits horaires contextuels
          (incompatibilité avec les AUTRES affectations du bénévole, pas avec p2 ↔ p1)

  3. FILL VALIDE PAR CONSTRUCTION (_fill_mutation)
     On tire dans eligible_benevoles[poste_id] directement.
     Seul le test de conflit horaire contextuel reste nécessaire.

  4. MUTATION EN CHAÎNE (_chain_swap_mutation) — NOUVEAU
     Échange en rotation de 3 bénévoles : b1→p2, b2→p3, b3→p1.
     Permet de sortir de configurations bloquées pour le swap binaire
     (b1 veut aller en p2 mais b2 ne peut pas aller en p1, sauf si b3
     peut aller en p1 à la place de b2).

  5. HILL-CLIMBING AMÉLIORÉ
     Voir hill_climber.py — le hill-climbing tente désormais un nombre
     significatif d'essais (attempts_per_move=50) avec restart aléatoire,
     et ne s'arrête qu'après max_no_improve passes sans aucune amélioration.

INVARIANT MAINTENU :
  Toute mutation retourne TOUJOURS un chromosome différent du parent
  (ou le parent original si vraiment aucune modification n'est possible).
  Le taux de mutation "effectif" (chromosomes réellement modifiés) est
  ainsi drastiquement amélioré vs v1.
"""
import random
import logging
from collections import defaultdict

from horizons_core.dataclass.poste import Poste
from horizons_genetic.genetic.core.chromosome import LightweightChromosome
from horizons_genetic.genetic.operators.mutation.i_mutation import MutationOperator
from horizons_genetic.genetic.fitness.affectation_scorer import ScoreCache
from horizons_genetic.genetic.utils.index_manager import IndexManager
from horizons_genetic.genetic.utils.daily_hours_checker import (
    compute_daily_hours,
    violates_daily_limit,
)

logger = logging.getLogger(__name__)


class AdaptiveMutation(MutationOperator):
    """
    Applique plusieurs mutations en respectant les contraintes dures
    par construction (indexation statique) plutôt que par rejet.
    """

    def __init__(
        self,
        postes:             list[Poste],
        index_manager:      IndexManager,
        base_mutation_rate: float = 0.06,
        max_retries:        int   = 10,   # gardé pour compatibilité, peu utilisé en v2
        all_benevole_ids:   set[int] | None = None,
        score_cache:        ScoreCache | None = None,
    ):
        self.postes             = postes
        self.index_manager      = index_manager
        self.base_mutation_rate = base_mutation_rate
        self.max_retries        = max_retries
        self.all_benevole_ids   = all_benevole_ids or set()
        self.score_cache        = score_cache or ScoreCache(index_manager)

        self.benevoles = [
            index_manager.id_to_benevole(i)
            for i in range(len(index_manager._id_to_benevole))
        ]

        # Index statiques (contraintes indépendantes du contexte)
        self.eligible_postes:    dict[int, list[int]] = {}   # b_id → [poste_ids disponibles]
        self.eligible_benevoles: dict[int, list[int]] = {}   # p_id → [b_ids disponibles]
        self.adjacent_postes:    dict[int, list[int]] = {}   # p_id → [poste_ids adjacents]
        self.postes_by_category: dict[int, list[int]] = {}   # pole_id → [poste_ids]

        # Index de compatibilité croisée pour les swaps : (b1_id, p2_id) → liste de
        # (p1_id, slot_idx) où b2 au slot_idx est disponible sur p2 ET b1 sur p1
        # Construit à la demande (trop volumineux à précalculer entièrement)
        self._build_structures()

        # Définition des types de mutation (fonction, probabilité)
        self.mutation_types = [
            (self._fill_mutation,        0.30),
            (self._swap_mutation,        0.25),
            (self._inject_mutation,      0.12),
            (self._shift_mutation,       0.10),
            (self._preference_mutation,  0.10),
            (self._chain_swap_mutation,  0.13),
        ]

    # ------------------------------------------------------------------
    # Construction des index statiques
    # ------------------------------------------------------------------

    def _build_structures(self) -> None:
        """Construit tous les index statiques à partir des données immutables."""
        all_b_ids = list(self.all_benevole_ids)
        all_p_ids = [self.index_manager.poste_to_id(p) for p in self.postes]

        # Index de disponibilité : O(B × P)
        for b_id in all_b_ids:
            benevole = self.index_manager.id_to_benevole(b_id)
            if benevole is None:
                self.eligible_postes[b_id] = []
                continue
            eligible = []
            for p_id in all_p_ids:
                poste = self.index_manager.id_to_poste(p_id)
                if poste and benevole.is_disponible(poste.get_horaire()):
                    eligible.append(p_id)
            self.eligible_postes[b_id] = eligible

        for p_id in all_p_ids:
            poste = self.index_manager.id_to_poste(p_id)
            if poste is None:
                self.eligible_benevoles[p_id] = []
                continue
            creneau  = poste.get_horaire()
            eligible = [
                b_id for b_id in all_b_ids
                if (benevole := self.index_manager.id_to_benevole(b_id)) is not None
                and benevole.is_disponible(creneau)
            ]
            self.eligible_benevoles[p_id] = eligible

        for p1 in self.postes:
            p1_id = self.index_manager.poste_to_id(p1)
            c1    = p1.get_horaire()
            self.adjacent_postes[p1_id] = [
                self.index_manager.poste_to_id(p2)
                for p2 in self.postes
                if p2 is not p1
                and c1.get_jour() == p2.get_horaire().get_jour()
                and (
                    c1.get_borne_sup() == p2.get_horaire().get_borne_inf()
                    or p2.get_horaire().get_borne_sup() == c1.get_borne_inf()
                )
            ]

        # Index par catégorie/pôle
        for p in self.postes:
            pole_id = p.get_categorie().pole_id
            p_id    = self.index_manager.poste_to_id(p)
            self.postes_by_category.setdefault(pole_id, []).append(p_id)

    # ------------------------------------------------------------------
    # Point d'entrée public
    # ------------------------------------------------------------------

    def mutate(self, chromosome: LightweightChromosome) -> LightweightChromosome:
        """
        Applique 2 à 4 mutations successives.
        Au moins 2 mutations sont toujours tentées.
        """
        mutated     = chromosome
        n_mutations = random.randint(2, 4)
        for i in range(n_mutations):
            if i >= 2 and random.random() > 0.6:
                break
            mutation_fn = self._select_mutation_type()
            mutated     = mutation_fn(mutated)
        return mutated

    def _select_mutation_type(self):
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

    def _conflicts_with_existing(
        self,
        b_id:        int,
        new_poste_id: int,
        assignments: dict[int, list[int]],
        exclude_poste_id: int | None = None,
    ) -> bool:
        """
        Vérifie si b_id a un conflit horaire avec ses affectations existantes
        (hors exclude_poste_id) si on l'affecte à new_poste_id.
        """
        new_c = self.index_manager.id_to_poste(new_poste_id).get_horaire()
        for other_pid in assignments.get(b_id, []):
            if other_pid == exclude_poste_id:
                continue
            if new_c.is_incompatible(self.index_manager.id_to_poste(other_pid).get_horaire()):
                return True
        return False

    def _daily_limit_ok(
        self,
        b_id:        int,
        new_poste_id: int,
        daily_hours: dict[int, dict[int, float]],
        old_poste_id: int | None = None,
    ) -> bool:
        """
        Vérifie la limite journalière si b_id est déplacé vers new_poste_id.
        Si old_poste_id est fourni, on soustrait d'abord la durée de ce poste.
        """
        new_c = self.index_manager.id_to_poste(new_poste_id).get_horaire()
        jour  = new_c.get_jour()
        duree = new_c.get_borne_sup() - new_c.get_borne_inf()

        sim = dict(daily_hours.get(b_id, {}))

        if old_poste_id is not None:
            old_c    = self.index_manager.id_to_poste(old_poste_id).get_horaire()
            old_jour = old_c.get_jour()
            old_dur  = old_c.get_borne_sup() - old_c.get_borne_inf()
            sim[old_jour] = sim.get(old_jour, 0.0) - old_dur

        return not violates_daily_limit(b_id, new_c, {b_id: sim}, self.index_manager)

    # ------------------------------------------------------------------
    # FILL — valide par construction via eligible_benevoles
    # ------------------------------------------------------------------

    def _fill_mutation(self, chromosome: LightweightChromosome) -> LightweightChromosome:
        """
        Remplit un slot vide avec le meilleur bénévole disponible.
        Tire directement dans eligible_benevoles[poste_id] : seule la
        vérification contextuelle (conflits horaires avec d'autres postes)
        reste nécessaire.
        """
        empty_slots = [
            (p_id, i)
            for p_id, bvs in chromosome.poste_to_benevoles.items()
            for i, b in enumerate(bvs)
            if b < 0
        ]
        if not empty_slots:
            return chromosome

        # Taux de remplissage → nombre de fills par mutation
        total     = chromosome.count_total_positions()
        filled    = chromosome.count_filled_positions()
        fill_rate = filled / total if total > 0 else 0.0
        max_fills = 4 if fill_rate < 0.70 else (2 if fill_rate < 0.85 else 1)

        daily_hours = compute_daily_hours(chromosome.poste_to_benevoles, self.index_manager)
        assignments = chromosome.get_benevole_assignments()
        assigned    = chromosome.get_assigned_benevoles()

        # Trier les slots vides par score maximal potentiel
        def best_score(p_id):
            return max(
                (self.score_cache.get(b_id, p_id) for b_id in self.eligible_benevoles.get(p_id, [])),
                default=0.0
            )

        random.shuffle(empty_slots)
        scored_slots = sorted(empty_slots[:max_fills * 4], key=lambda s: best_score(s[0]), reverse=True)

        mutated  = chromosome.clone()
        n_filled = 0

        for poste_id, slot in scored_slots:
            if n_filled >= max_fills:
                break

            # Candidates : disponibles sur ce poste (index statique)
            candidates = sorted(
                self.eligible_benevoles.get(poste_id, []),
                key=lambda b: self.score_cache.get(b, poste_id),
                reverse=True,
            )

            for b_id in candidates:
                if b_id in mutated.poste_to_benevoles.get(poste_id, []):
                    continue
                # Seuls les conflits contextuels restent à vérifier
                if self._conflicts_with_existing(b_id, poste_id, assignments):
                    continue
                if not self._daily_limit_ok(b_id, poste_id, daily_hours):
                    continue

                mutated.poste_to_benevoles[poste_id][slot] = b_id

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

    # ------------------------------------------------------------------
    # INJECT — bénévoles non affectés
    # ------------------------------------------------------------------

    def _inject_mutation(self, chromosome: LightweightChromosome) -> LightweightChromosome:
        """Place un bénévole non affecté dans un slot vide."""
        assigned   = chromosome.get_assigned_benevoles()
        unassigned = list(self.all_benevole_ids - assigned)
        if not unassigned:
            return chromosome

        empty_slots = [
            (p_id, i)
            for p_id, bvs in chromosome.poste_to_benevoles.items()
            for i, b in enumerate(bvs) if b < 0
        ]
        if not empty_slots:
            return chromosome

        daily_hours = compute_daily_hours(chromosome.poste_to_benevoles, self.index_manager)
        assignments = chromosome.get_benevole_assignments()

        # Trier par score décroissant pour maximiser la qualité de l'injection
        candidates = sorted(
            unassigned,
            key=lambda b: max(
                (self.score_cache.get(b, p_id) for p_id, _ in empty_slots),
                default=0.0
            ),
            reverse=True,
        )

        for b_id in candidates[:self.max_retries]:
            eligible_slots = [
                (p_id, slot) for p_id, slot in empty_slots
                if p_id in self.eligible_postes.get(b_id, set())
                and not self._conflicts_with_existing(b_id, p_id, assignments)
                and self._daily_limit_ok(b_id, p_id, daily_hours)
            ]
            if not eligible_slots:
                continue

            poste_id, slot = max(eligible_slots, key=lambda s: self.score_cache.get(b_id, s[0]))
            mutated = chromosome.clone()
            mutated.poste_to_benevoles[poste_id][slot] = b_id
            return mutated

        return chromosome

    # ------------------------------------------------------------------
    # SWAP — valide par construction via index croisé
    # ------------------------------------------------------------------

    def _swap_mutation(self, chromosome: LightweightChromosome) -> LightweightChromosome:
        """
        Échange b1 (dans p1) et b2 (dans p2).

        Construction valide :
          1. Tire b1 dans un poste occupé p1
          2. Filtre les postes p2 où b1 EST disponible (index statique)
             ET dont les bénévoles en place sont disponibles sur p1
          3. Vérifie les conflits contextuels seulement sur la liste filtrée
        """
        all_p_ids = list(chromosome.poste_to_benevoles.keys())
        if len(all_p_ids) < 2:
            return chromosome

        daily_hours = compute_daily_hours(chromosome.poste_to_benevoles, self.index_manager)
        assignments = chromosome.get_benevole_assignments()

        # Mélanger pour diversité
        random.shuffle(all_p_ids)

        for p1_id in all_p_ids[:20]:   # Tester au plus 20 postes sources
            bvs1  = chromosome.poste_to_benevoles[p1_id]
            valid = [b for b in bvs1 if b >= 0]
            if not valid:
                continue

            b1_id = random.choice(valid)
            idx1  = bvs1.index(b1_id)

            # Postes candidats pour p2 : b1 doit être disponible sur p2
            b1_eligible_postes = set(self.eligible_postes.get(b1_id, []))

            # Filtrer les postes p2 où un bénévole est présent et disponible sur p1
            eligible_p1_benevoles = set(self.eligible_benevoles.get(p1_id, []))

            candidates_p2 = [
                p_id for p_id in all_p_ids
                if p_id != p1_id
                and p_id in b1_eligible_postes
                and any(
                    b in eligible_p1_benevoles
                    for b in chromosome.poste_to_benevoles.get(p_id, [])
                    if b >= 0
                )
            ]

            if not candidates_p2:
                continue

            random.shuffle(candidates_p2)

            for p2_id in candidates_p2[:10]:
                bvs2 = chromosome.poste_to_benevoles[p2_id]

                # Trouver un b2 disponible sur p1
                eligible_b2 = [
                    (i, b) for i, b in enumerate(bvs2)
                    if b in eligible_p1_benevoles
                ]
                if not eligible_b2:
                    continue

                idx2, b2_id = random.choice(eligible_b2)

                # Vérifier les conflits contextuels (les conflits statiques sont déjà éliminés)
                b1_ok = not self._conflicts_with_existing(b1_id, p2_id, assignments, exclude_poste_id=p1_id)
                b1_ok = b1_ok and self._daily_limit_ok(b1_id, p2_id, daily_hours, old_poste_id=p1_id)

                if b2_id >= 0:
                    b2_ok = not self._conflicts_with_existing(b2_id, p1_id, assignments, exclude_poste_id=p2_id)
                    b2_ok = b2_ok and self._daily_limit_ok(b2_id, p1_id, daily_hours, old_poste_id=p2_id)
                else:
                    b2_ok = True   # slot vide → pas de contraintes sur b2

                if b1_ok and b2_ok:
                    mutated = chromosome.clone()
                    mutated.poste_to_benevoles[p1_id][idx1] = b2_id
                    mutated.poste_to_benevoles[p2_id][idx2] = b1_id
                    return mutated

        return chromosome

    # ------------------------------------------------------------------
    # CHAIN SWAP — échange en rotation de 3 bénévoles (NOUVEAU)
    # ------------------------------------------------------------------

    def _chain_swap_mutation(self, chromosome: LightweightChromosome) -> LightweightChromosome:
        """
        Échange en chaîne : b1→p2, b2→p3, b3→p1.

        Permet de sortir des configurations où aucun swap binaire n'est
        possible mais où une rotation à 3 est valide.
        Exemple : b1 veut aller en p2, b2 veut aller en p3, b3 peut remplir p1.
        """
        all_p_ids = list(chromosome.poste_to_benevoles.keys())
        if len(all_p_ids) < 3:
            return chromosome

        daily_hours = compute_daily_hours(chromosome.poste_to_benevoles, self.index_manager)
        assignments = chromosome.get_benevole_assignments()

        for _ in range(15):  # 15 tentatives aléatoires
            p1_id, p2_id, p3_id = random.sample(all_p_ids, 3)

            bvs1 = [b for b in chromosome.poste_to_benevoles[p1_id] if b >= 0]
            bvs2 = [b for b in chromosome.poste_to_benevoles[p2_id] if b >= 0]
            bvs3 = [b for b in chromosome.poste_to_benevoles[p3_id] if b >= 0]

            if not bvs1 or not bvs2 or not bvs3:
                continue

            b1_id = random.choice(bvs1)
            b2_id = random.choice(bvs2)
            b3_id = random.choice(bvs3)

            # Vérifier la disponibilité statique (index) pour les 3 mouvements
            b1_elig = set(self.eligible_postes.get(b1_id, []))
            b2_elig = set(self.eligible_postes.get(b2_id, []))
            b3_elig = set(self.eligible_postes.get(b3_id, []))

            if p2_id not in b1_elig or p3_id not in b2_elig or p1_id not in b3_elig:
                continue

            # Vérifier les conflits contextuels pour les 3 mouvements
            ok = (
                not self._conflicts_with_existing(b1_id, p2_id, assignments, exclude_poste_id=p1_id)
                and self._daily_limit_ok(b1_id, p2_id, daily_hours, old_poste_id=p1_id)
                and not self._conflicts_with_existing(b2_id, p3_id, assignments, exclude_poste_id=p2_id)
                and self._daily_limit_ok(b2_id, p3_id, daily_hours, old_poste_id=p2_id)
                and not self._conflicts_with_existing(b3_id, p1_id, assignments, exclude_poste_id=p3_id)
                and self._daily_limit_ok(b3_id, p1_id, daily_hours, old_poste_id=p3_id)
            )

            if ok:
                mutated = chromosome.clone()
                idx1 = chromosome.poste_to_benevoles[p1_id].index(b1_id)
                idx2 = chromosome.poste_to_benevoles[p2_id].index(b2_id)
                idx3 = chromosome.poste_to_benevoles[p3_id].index(b3_id)
                mutated.poste_to_benevoles[p1_id][idx1] = b3_id
                mutated.poste_to_benevoles[p2_id][idx2] = b1_id
                mutated.poste_to_benevoles[p3_id][idx3] = b2_id
                return mutated

        return chromosome

    # ------------------------------------------------------------------
    # SHIFT — poste adjacent
    # ------------------------------------------------------------------

    def _shift_mutation(self, chromosome: LightweightChromosome) -> LightweightChromosome:
        """Déplace un bénévole vers un poste temporellement adjacent."""
        occupied = [
            p_id for p_id in chromosome.poste_to_benevoles
            if any(b >= 0 for b in chromosome.poste_to_benevoles[p_id])
        ]
        if not occupied:
            return chromosome

        daily_hours = compute_daily_hours(chromosome.poste_to_benevoles, self.index_manager)
        assignments = chromosome.get_benevole_assignments()

        random.shuffle(occupied)
        for p1_id in occupied[:15]:
            adj = self.adjacent_postes.get(p1_id, [])
            if not adj:
                continue

            bvs1  = chromosome.poste_to_benevoles[p1_id]
            valid = [b for b in bvs1 if b >= 0]
            if not valid:
                continue

            b1_id = random.choice(valid)
            idx1  = bvs1.index(b1_id)
            b1_elig = set(self.eligible_postes.get(b1_id, []))

            # Filtrer les postes adjacents où b1 est disponible
            eligible_adj = [p for p in adj if p in b1_elig]
            if not eligible_adj:
                continue

            for p2_id in random.sample(eligible_adj, min(5, len(eligible_adj))):
                bvs2 = chromosome.poste_to_benevoles[p2_id]
                idx2 = random.randint(0, len(bvs2) - 1)
                b2_id = bvs2[idx2]

                b1_ok = (
                    not self._conflicts_with_existing(b1_id, p2_id, assignments, exclude_poste_id=p1_id)
                    and self._daily_limit_ok(b1_id, p2_id, daily_hours, old_poste_id=p1_id)
                )

                if b2_id >= 0:
                    b2_elig = set(self.eligible_postes.get(b2_id, []))
                    b2_ok = (
                        p1_id in b2_elig
                        and not self._conflicts_with_existing(b2_id, p1_id, assignments, exclude_poste_id=p2_id)
                        and self._daily_limit_ok(b2_id, p1_id, daily_hours, old_poste_id=p2_id)
                    )
                else:
                    b2_ok = True

                if b1_ok and b2_ok:
                    mutated = chromosome.clone()
                    mutated.poste_to_benevoles[p1_id][idx1] = b2_id
                    mutated.poste_to_benevoles[p2_id][idx2] = b1_id
                    return mutated

        return chromosome

    # ------------------------------------------------------------------
    # PREFERENCE — même catégorie
    # ------------------------------------------------------------------

    def _preference_mutation(self, chromosome: LightweightChromosome) -> LightweightChromosome:
        """Échange deux bénévoles dans la même catégorie (améliore les préférences)."""
        eligible_poles = [
            pole_id for pole_id, ids in self.postes_by_category.items()
            if len(ids) >= 2
        ]
        if not eligible_poles:
            return chromosome

        daily_hours = compute_daily_hours(chromosome.poste_to_benevoles, self.index_manager)
        assignments = chromosome.get_benevole_assignments()

        random.shuffle(eligible_poles)
        for pole_id in eligible_poles[:5]:
            pool = self.postes_by_category[pole_id]
            if len(pool) < 2:
                continue

            random.shuffle(pool)
            for p1_id in pool[:10]:
                bvs1  = chromosome.poste_to_benevoles.get(p1_id, [])
                valid = [b for b in bvs1 if b >= 0]
                if not valid:
                    continue

                b1_id   = random.choice(valid)
                idx1    = bvs1.index(b1_id)
                b1_elig = set(self.eligible_postes.get(b1_id, []))

                # Trouver p2 dans la même catégorie où b1 est disponible
                eligible_p2 = [
                    p_id for p_id in pool
                    if p_id != p1_id and p_id in b1_elig
                ]
                if not eligible_p2:
                    continue

                p2_id = random.choice(eligible_p2)
                bvs2  = chromosome.poste_to_benevoles.get(p2_id, [])
                if not bvs2:
                    continue

                idx2  = random.randint(0, len(bvs2) - 1)
                b2_id = bvs2[idx2]

                b1_ok = (
                    not self._conflicts_with_existing(b1_id, p2_id, assignments, exclude_poste_id=p1_id)
                    and self._daily_limit_ok(b1_id, p2_id, daily_hours, old_poste_id=p1_id)
                )

                if b2_id >= 0:
                    b2_elig = set(self.eligible_postes.get(b2_id, []))
                    b2_ok = (
                        p1_id in b2_elig
                        and not self._conflicts_with_existing(b2_id, p1_id, assignments, exclude_poste_id=p2_id)
                        and self._daily_limit_ok(b2_id, p1_id, daily_hours, old_poste_id=p2_id)
                    )
                else:
                    b2_ok = True

                if b1_ok and b2_ok:
                    mutated = chromosome.clone()
                    mutated.poste_to_benevoles[p1_id][idx1] = b2_id
                    mutated.poste_to_benevoles[p2_id][idx2] = b1_id
                    return mutated

        return chromosome