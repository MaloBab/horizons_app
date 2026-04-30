"""
Crossover par bénévole (Volunteer-Centric Crossover).

STRATÉGIE :
  Plutôt que de copier poste par poste (uniforme), on copie le planning
  COMPLET d'un bénévole depuis un seul parent.

  Pour chaque bénévole, on choisit aléatoirement (50/50) d'hériter
  toutes ses affectations depuis parent1 ou parent2.

AVANTAGE CLÉ vs crossover uniforme :
  Un bénévole affecté à plusieurs postes (double-affectation créée par
  _fill_mutation) est transmis INTACT. Le crossover uniforme cassait
  ces doubles-affectations en copiant poste par poste depuis des parents
  différents, produisant des conflits horaires que la réparation résolvait
  en vidant des slots — annulant le travail de _fill_mutation.

OPTIMISATION — ScoreCache :
  Les appels à score_affectation() pour choisir le meilleur parent source
  et résoudre les conflits de slots utilisent score_cache.get() — O(1).
"""
import random
import logging
from collections import defaultdict

from horizons_genetic.genetic.core.chromosome import LightweightChromosome
from horizons_genetic.genetic.operators.crossover.i_crossover import CrossoverOperator
from horizons_genetic.genetic.fitness.affectation_scorer import ScoreCache
from horizons_genetic.genetic.utils.index_manager import IndexManager

logger = logging.getLogger(__name__)


class VolunteerCrossover(CrossoverOperator):
    """
    Crossover par bénévole : chaque bénévole hérite son planning complet
    depuis un seul parent, préservant les doubles-affectations valides.
    """

    def __init__(self, index_manager: IndexManager, score_cache: ScoreCache | None = None):
        self.index_manager = index_manager
        # Cache partagé depuis GeneticEngine
        self.score_cache = score_cache or ScoreCache(index_manager)

    def crossover(
        self,
        parent1: LightweightChromosome,
        parent2: LightweightChromosome,
    ) -> LightweightChromosome:
        # ── 1. Index des affectations par bénévole dans chaque parent ──
        p1_assignments = self._index_by_benevole(parent1)
        p2_assignments = self._index_by_benevole(parent2)

        all_benevole_ids = set(p1_assignments.keys()) | set(p2_assignments.keys())

        # ── 2. Construction de l'enfant bénévole par bénévole ─────────
        child_slots: dict[int, dict[int, int]] = {
            poste_id: {i: -1 for i in range(len(benevoles))}
            for poste_id, benevoles in parent1.poste_to_benevoles.items()
        }

        # File d'attente : (score, benevole_id, poste_id, slot_index)
        pending: list[tuple[float, int, int, int]] = []

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
                # Les deux parents ont des affectations : choisir le meilleur
                score1 = sum(self.score_cache.get(b_id, pid) for pid in p1_postes)
                score2 = sum(self.score_cache.get(b_id, pid) for pid in p2_postes)
                # Biais aléatoire léger pour maintenir la diversité
                if random.random() < 0.15:
                    source = random.choice([p1_postes, p2_postes])
                else:
                    source = p1_postes if score1 >= score2 else p2_postes

            for poste_id, slot_idx in source.items():
                if poste_id in child_slots:
                    sc = self.score_cache.get(b_id, poste_id)
                    pending.append((sc, b_id, poste_id, slot_idx))

        # ── 3. Résolution des conflits de slot ────────────────────────
        pending.sort(key=lambda x: x[0], reverse=True)

        for sc, b_id, poste_id, slot_idx in pending:
            slots = child_slots[poste_id]

            if b_id in slots.values():
                continue

            if slots.get(slot_idx, -1) == -1:
                slots[slot_idx] = b_id
            else:
                free_slot = next((i for i, v in slots.items() if v == -1), None)
                if free_slot is not None:
                    slots[free_slot] = b_id

        # ── 4. Convertir en structure LightweightChromosome ───────────
        child_affectations = {
            poste_id: [slots[i] for i in range(len(slots))]
            for poste_id, slots in child_slots.items()
        }

        return LightweightChromosome(poste_to_benevoles=child_affectations)

    # ------------------------------------------------------------------

    def _index_by_benevole(
        self,
        chromosome: LightweightChromosome,
    ) -> dict[int, dict[int, int]]:
        """
        Construit un index : benevole_id → {poste_id: slot_index}.
        """
        index: dict[int, dict[int, int]] = defaultdict(dict)
        for poste_id, benevole_ids in chromosome.poste_to_benevoles.items():
            for slot_idx, b_id in enumerate(benevole_ids):
                if b_id >= 0 and poste_id not in index[b_id]:
                    index[b_id][poste_id] = slot_idx
        return dict(index)