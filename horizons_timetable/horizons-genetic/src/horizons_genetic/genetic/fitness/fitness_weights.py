"""
Poids pour le calcul de fitness.

PHILOSOPHIE — FITNESS TOUT-BONUS + PÉNALITÉS CIBLÉES :
  Le GA compare des solutions entre elles, pas contre un absolu.

  On encode UNIQUEMENT des récompenses positives et des pénalités
  proportionnelles à l'écart par rapport à l'idéal :

    ✅  poste rempli              → reward (signal le plus fort)
    ✅  préférence respectée      → reward
    ✅  compagnons ensemble       → reward
    ✅  charge équilibrée         → reward (bénévole bien utilisé)
    ⛔  bénévole non affecté      → pénalité (moins grave qu'un poste vide)
    ⛔  consécutifs excessifs     → pénalité au-delà du seuil raisonnable
    ⛔  violation horaire         → pénalité GRADUÉE (proportionnelle à l'excès)

  SUPPRESSION DE benevole_affecte (bonus) :
    L'ancien bonus "bénévole affecté" saturait rapidement (dès que tous les
    bénévoles avaient au moins un poste, le signal devenait une constante
    et ne guidait plus le GA). Il est remplacé par une PÉNALITÉ proportionnelle
    au nombre de bénévoles laissés sans rôle — ce gradient reste actif toute
    l'évolution, y compris en fin de convergence.

  CALIBRATION DES PRIORITÉS (ordre décroissant) :
    1. Couverture opérationnelle   : position_remplie (200)
    2. Satisfaction individuelle   : compagnon (180), préférences (120)
    3. Équité collective           : charge_bien_utilisee (60)
    4. Bénévoles non affectés      : benevole_non_affecte (-90)
       → Moins grave qu'un poste vide (corrigeable à la main)
       → Assez fort pour maintenir un gradient actif
    5. Confort                     : pénalité créneaux consécutifs excessifs
    6. Contrainte dure             : pénalité violation horaire graduée
"""
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Limites horaires journalières par type — CONTRAINTES DURES
MAX_HOURS_NORMAL:     int = 6
MAX_HOURS_SPECIALISE: int = 2


@dataclass
class FitnessWeights:
    """Poids pour le calcul de fitness — bonus positifs + pénalités graduées."""

    # ── Couverture opérationnelle ─────────────────────────────────────
    position_remplie:    float = 200.0   # Poste pourvu → signal le plus fort

    # ── Satisfaction individuelle ─────────────────────────────────────
    preference_match:             float = 120.0  # Rang 1 = 120 × n_prefs, rang 2 = 120 × (n-1)…
    compagnon_travaille_ensemble: float = 180.0  # Par paire de compagnons réunis

    # ── Équité collective ─────────────────────────────────────────────
    # Récompense quand la charge d'un bénévole est ≥ 1h et ≤ (limite - 1h).
    charge_bien_utilisee: float = 60.0

    # ── Bénévoles non affectés ────────────────────────────────────────
    # Pénalité par bénévole laissé sans aucun rôle.
    # Calibrée en dessous de position_remplie (un poste vide est plus grave
    # car non corrigeable automatiquement, contrairement à une affectation manuelle).
    benevole_non_affecte: float = 90.0   # valeur positive — signe négatif appliqué dans le calcul

    # ── Confort (malus créneaux consécutifs excessifs) ────────────────
    # Les créneaux jusqu'au seuil_consecutifs sont normaux et non pénalisés.
    # La pénalité s'applique uniquement à partir du (seuil + 1)e créneau consécutif.
    creneaux_consecutifs_excessifs:      float = -80.0
    creneaux_consecutifs_nuit_excessifs: float = -140.0

    # Seuil : nombre de paires consécutives à partir duquel on pénalise
    # (1 paire = 2 créneaux qui se touchent, 2 paires = 3 créneaux, etc.)
    seuil_consecutifs: int = 2  # 1 ou 2 paires consécutives = OK, 3+ = pénalité

    # ── Contrainte dure : violation horaire journalière ───────────────
    # Pénalité par heure d'excès au-delà de la limite journalière.
    # Calibrée au-dessus de position_remplie pour décourager les violations,
    # mais finie pour que le GA puisse comparer des solutions partiellement invalides.
    violation_horaire_par_heure: float = -2_000.0


@dataclass
class GradualFitnessWeights(FitnessWeights):
    """
    Poids avec pénalités graduelles (quadratiques) pour les créneaux
    consécutifs excessifs. La violation horaire reste linéaire avec l'excès.
    """

    def calculate_consecutive_penalty(
        self, num_consecutive: int, is_night: bool
    ) -> float:
        """
        Pénalité uniquement si num_consecutive > seuil_consecutifs.
        Croissante quadratiquement au-delà du seuil.

        num_consecutive ici représente le nombre de PAIRES consécutives
        (= nombre de transitions entre créneaux qui se touchent) :
          1 paire  → 2 créneaux qui se touchent      → OK
          2 paires → 3 créneaux consécutifs           → OK (seuil = 2)
          3 paires → 4 créneaux consécutifs           → pénalité

        Exemples (seuil = 2) :
          num_consecutive = 1 → excess = -1 → 0.0
          num_consecutive = 2 → excess =  0 → 0.0
          num_consecutive = 3 → excess =  1 → base * 1^1.5 = base
          num_consecutive = 4 → excess =  2 → base * 2^1.5 ≈ base * 2.83
        """
        excess = num_consecutive - self.seuil_consecutifs
        if excess <= 0:
            return 0.0
        base = (
            self.creneaux_consecutifs_nuit_excessifs
            if is_night
            else self.creneaux_consecutifs_excessifs
        )
        return base * (excess ** 1.5)

    def calculate_daily_violation_penalty(
        self, excess_hours: float
    ) -> float:
        """
        Pénalité graduée pour dépassement de la limite horaire journalière.

        Args:
            excess_hours: Nombre d'heures au-delà de la limite (> 0).

        Returns:
            float ≤ 0 — pénalité (négative).

        Exemples :
          1h d'excès   → -2 000.0
          2h d'excès   → -4 000.0
        """
        if excess_hours <= 0.0:
            return 0.0
        return self.violation_horaire_par_heure * excess_hours