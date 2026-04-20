"""
Utilitaire partagé : score d'une affectation (bénévole, poste).

Utilisé par tous les opérateurs de crossover et le GreedyCrossover
pour classer les affectations lors de la résolution de conflits
et de la construction greedy.

CORRECTION BUG PRÉFÉRENCES :
  La comparaison directe `pref_str == Categorie` ne fonctionne pas.
  On utilise PREFERENCES_TO_POSTES pour résoudre str → set[pole_id].
"""
from horizons_core.utils.enums import PREFERENCES_TO_POSTES
from horizons_genetic.genetic.utils.index_manager import IndexManager

# Pré-calcul une seule fois au chargement du module
_PREF_TO_POLE_IDS: dict[str, frozenset[int]] = {
    pref: frozenset(pole.value for pole in poles)
    for pref, poles in PREFERENCES_TO_POSTES.items()
}


def score_affectation(
    b_id:          int,
    poste_id:      int,
    index_manager: IndexManager,
    disponibilite_bonus: float = 5.0,
    pref_base_score:     float = 15.0,
) -> float:
    """
    Score une affectation (b_id, poste_id).

    Returns:
        float ≥ 0 — plus haut = meilleure adéquation.
    """
    benevole = index_manager.id_to_benevole(b_id)
    poste    = index_manager.id_to_poste(poste_id)
    score    = 0.0

    if benevole is None or poste is None:
        return score

    # Bonus disponibilité
    if benevole.is_disponible(poste.get_horaire()):
        score += disponibilite_bonus

    # Bonus préférence (via PREFERENCES_TO_POSTES)
    pole_id = poste.get_categorie().pole_id
    prefs   = benevole.get_preferences()  # list[str]
    n       = len(prefs)
    for rank, pref_str in enumerate(prefs):
        if pole_id in _PREF_TO_POLE_IDS.get(pref_str, frozenset()):
            score += pref_base_score - rank
            break

    return score