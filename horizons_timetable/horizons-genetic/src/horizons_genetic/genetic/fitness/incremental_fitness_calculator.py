"""
Calcul du fitness d'un chromosome.

SCORES DE FITNESS (tout-bonus sauf pénalités ciblées) :
  + position_remplie       : chaque position de poste occupée
  + preference_match       : adéquation bénévole ↔ pôle (via PREFERENCES_TO_POSTES)
  + compagnon_ensemble     : paires de compagnons réunies sur le même poste
  + charge_bien_utilisee   : bénévole dont la charge est ≥ 1h et ≤ (limite - 1h)
  - benevole_non_affecte   : pénalité par bénévole sans aucun rôle
  - consecutifs_excessifs  : malus si plus de `seuil_consecutifs` paires consécutives
  - violation_horaire      : pénalité graduée par heure d'excès

OPTIMISATION MÉMOIRE — store_raw :
  Le paramètre store_raw (défaut False) contrôle si le dict détaillé des scores
  est conservé dans le chromosome. Pendant l'évolution, on n'en a pas besoin :
  seul le scalaire fitness guide la sélection. On ne stocke les raw_scores que
  pour le meilleur individu final (pour les logs/statistiques).

  Gain : ~6 dict Python × taille_population alloués/libérés par génération en
  moins, ce qui réduit la pression GC sur un Raspberry Pi.
"""
from horizons_core.utils.enums import PREFERENCES_TO_POSTES
from horizons_genetic.genetic.fitness.fitness_weights import GradualFitnessWeights
from horizons_genetic.genetic.core.chromosome import LightweightChromosome
from horizons_genetic.genetic.utils.index_manager import IndexManager
from horizons_genetic.genetic.utils.daily_hours_checker import (
    compute_daily_violation_penalty,
    compute_daily_hours,
    get_daily_limit,
)


# Pré-calcul : preference_str → frozenset[pole_id (int)]
_PREF_TO_POLE_IDS: dict[str, frozenset[int]] = {
    pref: frozenset(pole.value for pole in poles)
    for pref, poles in PREFERENCES_TO_POSTES.items()
}


class IncrementalFitnessCalculator:
    """
    Calcule le fitness d'un chromosome.

    Fitness = somme de bonus positifs
              - pénalité bénévoles non affectés
              - pénalité créneaux consécutifs excessifs
              - pénalité violations horaires journalières
    """

    def __init__(self, weights: GradualFitnessWeights, index_manager: IndexManager):
        self.weights       = weights or GradualFitnessWeights()
        self.index_manager = index_manager

    # ------------------------------------------------------------------
    # Point d'entrée public
    # ------------------------------------------------------------------

    def calculate(
        self,
        chromosome: LightweightChromosome,
        all_benevole_ids: set[int],
        store_raw: bool = False,
    ) -> float:
        """
        Calcule et stocke le fitness du chromosome. Retourne la valeur.

        Args:
            chromosome:       Chromosome à évaluer.
            all_benevole_ids: Ensemble de tous les IDs bénévoles.
            store_raw:        Si True, stocke le dict détaillé des scores dans le
                              chromosome (utile uniquement pour le meilleur final).
                              Par défaut False pour économiser la mémoire pendant
                              l'évolution.
        """

        # ── Contrainte dure : limites horaires ────────────────────────
        violation_penalty = compute_daily_violation_penalty(
            chromosome.poste_to_benevoles, self.index_manager, self.weights
        )

        # ── Scores positifs + pénalités ciblées ──────────────────────
        scores = self._calculate_scores(chromosome, all_benevole_ids)

        total = sum(scores.values()) + violation_penalty

        if store_raw:
            chromosome.set_fitness(total, {**scores, 'violation_horaire': violation_penalty})
        else:
            chromosome.set_fitness(total, None)

        return total

    # ------------------------------------------------------------------
    # Calcul détaillé
    # ------------------------------------------------------------------

    def _calculate_scores(
        self,
        chromosome: LightweightChromosome,
        all_benevole_ids: set[int],
    ) -> dict[str, float]:
        scores: dict[str, float] = {}

        assigned = chromosome.get_assigned_benevoles()

        # ── 1. Couverture opérationnelle ─────────────────────────────
        filled = chromosome.count_filled_positions()
        scores['positions_remplies'] = filled * self.weights.position_remplie

        # ── 2. Bénévoles non affectés (pénalité) ─────────────────────
        unassigned_count = len(all_benevole_ids) - len(assigned)
        scores['benevoles_non_affectes'] = -unassigned_count * self.weights.benevole_non_affecte

        # ── 3. Préférences (bug corrigé via PREFERENCES_TO_POSTES) ───
        scores['preferences'] = self._score_preferences(chromosome)

        # ── 4. Compagnonnage ─────────────────────────────────────────
        scores['compagnonnage'] = self._score_companions(chromosome)

        # ── 5. Équité — charge bien utilisée ─────────────────────────
        scores['charge_bien_utilisee'] = self._score_workload_equity(
            chromosome, all_benevole_ids
        )

        # ── 6. Pénalité créneaux consécutifs excessifs ───────────────
        scores['creneaux_consecutifs'] = self._score_consecutive_slots(chromosome)

        return scores

    # ------------------------------------------------------------------
    # Scores individuels
    # ------------------------------------------------------------------

    def _score_preferences(self, chromosome: LightweightChromosome) -> float:
        """
        Récompense l'adéquation bénévole ↔ pôle.

          1. Récupérer le pole_id du poste (int).
          2. Pour chaque préférence déclarée (str), résoudre en frozenset[pole_id].
          3. Si le pole_id du poste est dans l'ensemble → match.
          4. Score proportionnel au rang (préférence 1 vaut plus que préférence 2).
        """
        score = 0.0
        for poste_id, benevole_ids in chromosome.poste_to_benevoles.items():
            poste   = self.index_manager.id_to_poste(poste_id)
            pole_id = poste.get_categorie().pole_id

            for b_id in benevole_ids:
                if b_id < 0:
                    continue
                benevole = self.index_manager.id_to_benevole(b_id)
                if benevole is None:
                    continue

                prefs = benevole.get_preferences()
                n     = len(prefs)
                for rank, pref_str in enumerate(prefs):
                    pole_ids_for_pref = _PREF_TO_POLE_IDS.get(pref_str, frozenset())
                    if pole_id in pole_ids_for_pref:
                        score += (n - rank) * self.weights.preference_match
                        break  # On ne compte que la meilleure préférence matchée

        return score

    def _score_companions(self, chromosome: LightweightChromosome) -> float:
        """Récompense les paires de compagnons réunies sur un même poste."""
        score = 0.0
        for benevole_ids in chromosome.poste_to_benevoles.values():
            valid_ids = [b_id for b_id in benevole_ids if b_id >= 0]
            for i, b_id in enumerate(valid_ids):
                benevole   = self.index_manager.id_to_benevole(b_id)
                compagnons = benevole.get_compagnons() if benevole else set()
                if not compagnons:
                    continue
                for other_id in valid_ids[i + 1:]:
                    other = self.index_manager.id_to_benevole(other_id)
                    if other in compagnons:
                        score += self.weights.compagnon_travaille_ensemble / len(compagnons)
        return score

    def _score_workload_equity(
        self,
        chromosome: LightweightChromosome,
        all_benevole_ids: set[int],
    ) -> float:
        """
        Équité de charge : itère sur TOUS les bénévoles (pas seulement les affectés).

        - Bénévole à 0h        → déjà pénalisé par benevole_non_affecte, pas de double pénalité ici
        - Charge dans [1h, limite-1h] → bonus charge_bien_utilisee
        - Charge = limite ou > → pas de bonus (ni pénalité ici, la violation horaire gère l'excès)
        """
        score       = 0.0
        daily_hours = compute_daily_hours(chromosome.poste_to_benevoles, self.index_manager)

        for b_id in all_benevole_ids:
            hours_by_day = daily_hours.get(b_id, {})
            if not hours_by_day:
                continue
            limit = get_daily_limit(b_id, self.index_manager)
            for h in hours_by_day.values():
                if 1.0 <= h <= (limit - 1):
                    score += self.weights.charge_bien_utilisee

        return score

    def _score_consecutive_slots(self, chromosome: LightweightChromosome) -> float:
        """
        Pénalité pour créneaux consécutifs excessifs (contrainte souple).

        CORRECTION off-by-one :
          Le compteur consecutive démarre à 1 dès la première paire touchante.
          Avec seuil_consecutifs = 2 :
            2 créneaux (1 paire)  → consecutive=1 → excess=-1 → 0.0  ✅
            3 créneaux (2 paires) → consecutive=2 → excess= 0 → 0.0  ✅
            4 créneaux (3 paires) → consecutive=3 → excess= 1 → pénalité ✅
        """
        score = 0.0

        benevole_creneaux: dict[int, list] = {}
        for poste_id, benevole_ids in chromosome.poste_to_benevoles.items():
            poste   = self.index_manager.id_to_poste(poste_id)
            creneau = poste.get_horaire()
            for b_id in benevole_ids:
                if b_id >= 0:
                    benevole_creneaux.setdefault(b_id, []).append(creneau)

        for creneaux in benevole_creneaux.values():
            sorted_c    = sorted(creneaux, key=lambda c: (c.get_jour(), c.get_borne_inf()))
            consecutive = 0

            for i in range(len(sorted_c) - 1):
                c1, c2 = sorted_c[i], sorted_c[i + 1]
                if (
                    c1.get_jour() == c2.get_jour()
                    and c1.get_borne_sup() == c2.get_borne_inf()
                ):
                    consecutive += 1
                    is_night = c2.get_borne_inf() >= 23
                    score   += self.weights.calculate_consecutive_penalty(consecutive, is_night)
                else:
                    consecutive = 0

        return score