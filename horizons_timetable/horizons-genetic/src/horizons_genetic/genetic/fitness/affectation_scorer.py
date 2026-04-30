"""
Utilitaire partagé : score d'une affectation (bénévole, poste).

Utilisé par tous les opérateurs de crossover et le GreedyCrossover
pour classer les affectations lors de la résolution de conflits
et de la construction greedy.
"""
from horizons_core.utils.enums import PREFERENCES_TO_POSTES
from horizons_genetic.genetic.utils.index_manager import IndexManager

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


class ScoreCache:
    """
    Cache statique de la matrice de scores bénévole × poste.

    Construit en O(B × P) une seule fois, puis chaque accès est O(1).
    Remplace les appels répétés à score_affectation() dans les mutations
    et le crossover, qui sont les goulots d'étranglement CPU principaux.

    Utilisation typique :
        # Dans __init__ de GeneticEngine ou PopulationInitializer :
        self.score_cache = ScoreCache(self.index_manager)

        # Dans _fill_mutation, au lieu de :
        #   score_affectation(b_id, poste_id, self.index_manager)
        # Écrire :
        #   self.score_cache.get(b_id, poste_id)
    """

    def __init__(
        self,
        index_manager:      IndexManager,
        disponibilite_bonus: float = 5.0,
        pref_base_score:     float = 15.0,
    ):
        self._cache: dict[tuple[int, int], float] = {}

        all_b_ids = index_manager.get_all_benevole_ids()
        all_p_ids = index_manager.get_all_poste_ids()

        for b_id in all_b_ids:
            benevole = index_manager.id_to_benevole(b_id)
            if benevole is None:
                continue
            prefs   = benevole.get_preferences()
            n       = len(prefs)

            for p_id in all_p_ids:
                poste = index_manager.id_to_poste(p_id)
                if poste is None:
                    continue

                sc = 0.0

                if benevole.is_disponible(poste.get_horaire()):
                    sc += disponibilite_bonus

                pole_id = poste.get_categorie().pole_id
                for rank, pref_str in enumerate(prefs):
                    if pole_id in _PREF_TO_POLE_IDS.get(pref_str, frozenset()):
                        sc += pref_base_score - rank
                        break

                self._cache[(b_id, p_id)] = sc

    def get(self, b_id: int, poste_id: int) -> float:
        """Retourne le score précalculé, 0.0 si la paire est inconnue."""
        return self._cache.get((b_id, poste_id), 0.0)