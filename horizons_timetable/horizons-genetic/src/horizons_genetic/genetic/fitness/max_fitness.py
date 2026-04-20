"""
Calcul du fitness maximum théoriquement atteignable.

Aligné sur la fitness corrigée de IncrementalFitnessCalculator :
  - Suppression de benevole_affecte (remplacé par benevole_non_affecte pénalité)
  - Cas idéal pour benevole_non_affecte : 0 bénévole sans rôle → pénalité = 0
  - Cas idéal pour charge_bien_utilisee : chaque bénévole dans la plage idéale

Utilisé uniquement pour afficher un pourcentage d'avancement lisible
dans les logs et les statistiques — pas pour guider le GA.
"""
from dataclasses import dataclass

from horizons_core.dataclass.poste import Poste
from horizons_core.dataclass.benevole import Benevole
from horizons_genetic.genetic.fitness.fitness_weights import GradualFitnessWeights


@dataclass
class FitnessMaxInfo:
    """Informations sur le fitness maximum théorique."""
    max_total:          float
    max_positions:      float
    max_preferences:    float
    max_compagnonnage:  float
    max_equite:         float

    # Détail des pénalités dans le cas idéal (toutes à 0)
    penalite_non_affectes: float = 0.0  # 0 si tout le monde est affecté

    def to_percentage(self, fitness_actuel: float) -> float:
        """Convertit un fitness en pourcentage du maximum théorique."""
        if self.max_total <= 0:
            return 0.0
        return (fitness_actuel / self.max_total) * 100

    def format_breakdown(self) -> str:
        """Retourne une description lisible de la composition du max."""
        return (
            f"Max théorique : {self.max_total:,.0f}\n"
            f"  dont positions    : {self.max_positions:,.0f}\n"
            f"  dont préférences  : {self.max_preferences:,.0f}\n"
            f"  dont compagnons   : {self.max_compagnonnage:,.0f}\n"
            f"  dont équité       : {self.max_equite:,.0f}\n"
            f"  pénalité non-aff. : {self.penalite_non_affectes:,.0f} (0 dans le cas idéal)"
        )


class FitnessMaxCalculator:
    """
    Calcule le fitness maximum théoriquement atteignable.

    Hypothèses optimales :
      - Toutes les positions remplies
      - Tous les bénévoles affectés (→ pénalité benevole_non_affecte = 0)
      - Chaque bénévole sur sa préférence de rang 1
      - Tous les compagnons réunis
      - Charge journalière de chaque bénévole dans la plage idéale
        (1h ≤ h ≤ limite - 1h) sur au moins un jour
      - Aucun créneau consécutif excessif (pénalité = 0)
      - Aucune violation horaire (pénalité = 0)
    """

    def __init__(self, weights: GradualFitnessWeights):
        self.weights = weights

    def calculate(
        self,
        postes:    list[Poste],
        benevoles: list[Benevole],
    ) -> FitnessMaxInfo:

        total_positions = sum(p.get_size() for p in postes)
        nb_benevoles    = len(benevoles)

        # ── Couverture ────────────────────────────────────────────────
        # Cas idéal : toutes les positions remplies
        max_positions = total_positions * self.weights.position_remplie

        # ── Bénévoles non affectés ────────────────────────────────────
        # Cas idéal : tous les bénévoles ont un rôle → pénalité = 0
        penalite_non_affectes = 0.0

        # ── Préférences ───────────────────────────────────────────────
        # Cas idéal : chaque bénévole affecté sur sa préférence de rang 1
        # (rank=0) → score = n_prefs * preference_match par affectation
        pref_len        = len(benevoles[0].get_preferences()) if benevoles else 0
        max_preferences = total_positions * pref_len * self.weights.preference_match

        # ── Compagnonnage ─────────────────────────────────────────────
        # Cas idéal : tous les compagnons réunis sur le même poste
        # Score par paire = compagnon_travaille_ensemble / nb_compagnons_du_benevole
        # On somme la contribution maximale de chaque bénévole :
        #   pour un bénévole avec k compagnons → k paires → k × (poids / k) = poids
        # Donc le max est simplement nb_benevoles_avec_compagnons × poids
        # (chaque bénévole contribue au plus une fois son poids, indépendamment de k)
        nb_avec_compagnons = sum(1 for b in benevoles if b.get_compagnons())
        max_compagnonnage  = nb_avec_compagnons * self.weights.compagnon_travaille_ensemble

        # ── Équité ────────────────────────────────────────────────────
        # Cas idéal : chaque bénévole a une charge idéale sur au moins un jour
        # (1h ≤ h ≤ limite - 1h) → un bonus par bénévole
        max_equite = nb_benevoles * self.weights.charge_bien_utilisee

        max_total = (
            max_positions
            + penalite_non_affectes   # 0 dans le cas idéal
            + max_preferences
            + max_compagnonnage
            + max_equite
        )

        return FitnessMaxInfo(
            max_total             = max_total,
            max_positions         = max_positions,
            max_preferences       = max_preferences,
            max_compagnonnage     = max_compagnonnage,
            max_equite            = max_equite,
            penalite_non_affectes = penalite_non_affectes,
        )


def format_fitness_percentage(
    fitness_actuel:   float,
    fitness_max_info: FitnessMaxInfo,
) -> str:
    """Formate le fitness en chaîne lisible avec pourcentage."""
    percentage = fitness_max_info.to_percentage(fitness_actuel)
    return (
        f"{fitness_actuel:,.0f} / {fitness_max_info.max_total:,.0f} "
        f"({percentage:.1f}%)"
    )   