"""
Crossover par bénévole — v2 : valide par construction.

STRATÉGIE v2 (vs v1) :
  Le crossover v1 construisait l'enfant bénévole par bénévole, puis résolvait
  les conflits de slots a posteriori de façon purement positionnelle (slot libre
  ou abandon). Il ne vérifiait pas les contraintes dures (disponibilité, conflits
  horaires, limite journalière) — c'était délégué à la mutation ou au fitness.

  v2 garantit que chaque affectation de l'enfant est valide par construction :

  1. HÉRITAGE PAR BÉNÉVOLE (identique à v1)
     Pour chaque bénévole, on choisit le parent qui lui offre le meilleur score
     total (via ScoreCache), avec un biais aléatoire de 15 % pour la diversité.

  2. RÉSOLUTION DE CONFLITS PAR PLANNING
     Avant d'écrire une affectation dans l'enfant, on vérifie :
       - Disponibilité du bénévole sur ce créneau
       - Pas de conflit horaire avec ses affectations déjà écrites dans l'enfant
       - Limite journalière respectée
     Si le bénévole est en conflit sur un poste hérité, on tente d'abord de
     trouver un slot alternatif sur ce même poste (même poste, slot différent).
     Sinon l'affectation est abandonnée proprement (slot reste -1).

  3. SLOT COMPÉTITIF
     Les affectations sont traitées par ordre décroissant de score (meilleurs
     en premier), ce qui maximise le fitness attendu tout en garantissant la
     validité.

COMPLEXITÉ :
  O(B × log B + P × S) où B = bénévoles, P = postes, S = slots par poste.
  Identique à v1 en pratique.
"""
import random
import logging
from collections import defaultdict

from horizons_genetic.genetic.core.chromosome import LightweightChromosome
from horizons_genetic.genetic.operators.crossover.i_crossover import CrossoverOperator
from horizons_genetic.genetic.fitness.affectation_scorer import ScoreCache
from horizons_genetic.genetic.utils.index_manager import IndexManager
from horizons_genetic.genetic.utils.daily_hours_checker import (
    compute_daily_hours,
    violates_daily_limit,
)

logger = logging.getLogger(__name__)


class VolunteerCrossover(CrossoverOperator):
    """
    Crossover par bénévole : chaque bénévole hérite son planning complet
    depuis un seul parent, avec validation de contraintes dures à l'écriture.
    """

    def __init__(self, index_manager: IndexManager, score_cache: ScoreCache | None = None):
        self.index_manager = index_manager
        self.score_cache   = score_cache or ScoreCache(index_manager)

    def crossover(
        self,
        parent1: LightweightChromosome,
        parent2: LightweightChromosome,
    ) -> LightweightChromosome:

        # ── 1. Index des affectations par bénévole ────────────────────
        p1_assignments = self._index_by_benevole(parent1)
        p2_assignments = self._index_by_benevole(parent2)
        all_benevole_ids = set(p1_assignments.keys()) | set(p2_assignments.keys())

        # ── 2. Choix de la source pour chaque bénévole ───────────────
        # (score, b_id, {poste_id: slot_idx})
        pending: list[tuple[float, int, dict[int, int]]] = []

        for b_id in all_benevole_ids:
            p1_postes = p1_assignments.get(b_id, {})
            p2_postes = p2_assignments.get(b_id, {})

            if not p1_postes and not p2_postes:
                continue
            elif not p1_postes:
                source = p2_postes
            elif not p2_postes:
                source = p1_postes
            else:
                score1 = sum(self.score_cache.get(b_id, pid) for pid in p1_postes)
                score2 = sum(self.score_cache.get(b_id, pid) for pid in p2_postes)
                if random.random() < 0.15:
                    source = random.choice([p1_postes, p2_postes])
                else:
                    source = p1_postes if score1 >= score2 else p2_postes

            total_score = sum(self.score_cache.get(b_id, pid) for pid in source)
            pending.append((total_score, b_id, source))

        # Traiter les meilleurs bénévoles en premier (maximise fitness enfant)
        pending.sort(key=lambda x: x[0], reverse=True)

        # ── 3. Construction de l'enfant avec validation à l'écriture ─
        # Structure de slots de l'enfant (initialisée vide)
        child_slots: dict[int, list[int]] = {
            poste_id: [-1] * len(benevoles)
            for poste_id, benevoles in parent1.poste_to_benevoles.items()
        }

        # Suivi des contraintes de l'enfant en construction
        child_daily_hours: dict[int, dict[int, float]] = {}
        child_assignments: dict[int, list[int]] = {}

        for _score, b_id, source in pending:
            for poste_id, preferred_slot in source.items():
                if poste_id not in child_slots:
                    continue
                # Vérifier la validité de cette affectation dans l'enfant
                if not self._is_valid(b_id, poste_id, child_daily_hours, child_assignments):
                    continue

                slots = child_slots[poste_id]

                # Essayer d'abord le slot préféré, puis n'importe quel slot libre
                slot_to_use = None
                if slots[preferred_slot] == -1:
                    slot_to_use = preferred_slot
                else:
                    free = next((i for i, v in enumerate(slots) if v == -1), None)
                    if free is not None:
                        slot_to_use = free

                if slot_to_use is None:
                    continue  # Poste plein, abandon propre

                # Écriture + mise à jour des structures de suivi
                slots[slot_to_use] = b_id
                self._update_tracking(b_id, poste_id, child_daily_hours, child_assignments)

        return LightweightChromosome(poste_to_benevoles=child_slots)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _is_valid(
        self,
        b_id:         int,
        poste_id:     int,
        daily_hours:  dict[int, dict[int, float]],
        assignments:  dict[int, list[int]],
    ) -> bool:
        """Vérifie disponibilité + conflits horaires + limite journalière."""
        benevole = self.index_manager.id_to_benevole(b_id)
        poste    = self.index_manager.id_to_poste(poste_id)
        if benevole is None or poste is None:
            return False

        creneau = poste.get_horaire()

        if not benevole.is_disponible(creneau):
            return False

        for other_pid in assignments.get(b_id, []):
            other_c = self.index_manager.id_to_poste(other_pid).get_horaire()
            if creneau.is_incompatible(other_c):
                return False

        if violates_daily_limit(b_id, creneau, daily_hours, self.index_manager):
            return False

        return True

    def _update_tracking(
        self,
        b_id:        int,
        poste_id:    int,
        daily_hours: dict[int, dict[int, float]],
        assignments: dict[int, list[int]],
    ) -> None:
        """Met à jour les structures de suivi après une affectation confirmée."""
        poste   = self.index_manager.id_to_poste(poste_id)
        creneau = poste.get_horaire()
        jour    = creneau.get_jour()
        duree   = creneau.get_borne_sup() - creneau.get_borne_inf()

        if b_id not in daily_hours:
            daily_hours[b_id] = {}
        daily_hours[b_id][jour] = daily_hours[b_id].get(jour, 0.0) + duree
        assignments.setdefault(b_id, []).append(poste_id)

    def _index_by_benevole(
        self,
        chromosome: LightweightChromosome,
    ) -> dict[int, dict[int, int]]:
        """Construit un index : benevole_id → {poste_id: slot_index}."""
        index: dict[int, dict[int, int]] = defaultdict(dict)
        for poste_id, benevole_ids in chromosome.poste_to_benevoles.items():
            for slot_idx, b_id in enumerate(benevole_ids):
                if b_id >= 0 and poste_id not in index[b_id]:
                    index[b_id][poste_id] = slot_idx
        return dict(index)