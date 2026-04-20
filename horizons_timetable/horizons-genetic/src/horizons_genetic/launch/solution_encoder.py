"""
Encodeur JSON dédié à la solution finale du pipeline Horizons.

Format produit :
{
    "generated_at": "2025-07-04T14:32:00",
    "statistics": {
        "benevoles_total": 120,
        "benevoles_assigned": 98,
        "positions_total": 200,
        "positions_filled": 185,
        "fill_rate_pct": 92.5,
        "overloaded_benevoles": 3
    },
    "assignments": [
        {
            "poste": {
                "name": "Accueil entrée",
                "category": "Accueil",
                "slot": {"day_index": 4, "start_time": 10, "end_time": 14}
            },
            "capacity": 3,
            "filled": 2,
            "benevoles": [
                {"first_name": "Alice", "last_name": "Martin", "email": "alice@example.fr"},
                {"first_name": "Bob",   "last_name": "Dupont", "email": "bob@example.fr"}
            ]
        }
    ]
}
"""
import json
from datetime import datetime
from enum import Enum
from typing import Any

from horizons_genetic.launch.config import MAX_HEURES_PAR_JOUR
from horizons_genetic.launch.statistics import compute_benevole_hours, find_overloaded


class SolutionJSONEncoder(json.JSONEncoder):
    """Sérialise un Chromosome en représentation JSON dédiée solution."""

    def default(self, o: Any) -> Any:
        if isinstance(o, Enum):
            return o.value
        return super().default(o)

    # ------------------------------------------------------------------
    # Point d'entrée principal
    # ------------------------------------------------------------------

    def encode_solution(self, solution: Any, benevoles_total: int) -> dict:
        """Construit le dict complet de la solution.

        Args:
            solution:        Chromosome validé.
            benevoles_total: Nombre de bénévoles parsés (pour le taux).

        Returns:
            dict sérialisable via json.dumps(obj, cls=SolutionJSONEncoder).
        """
        return {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "statistics":   self._build_statistics(solution, benevoles_total),
            "assignments":  self._build_assignments(solution),
        }

    # ------------------------------------------------------------------
    # Blocs privés
    # ------------------------------------------------------------------

    def _build_statistics(self, solution: Any, benevoles_total: int) -> dict:
        assigned = solution.get_assigned_benevoles()
        filled   = solution.count_filled_positions()
        total    = solution.count_total_positions()

        benevole_hours = compute_benevole_hours(solution)
        overloaded     = find_overloaded(benevole_hours, MAX_HEURES_PAR_JOUR)

        return {
            "benevoles_total":    benevoles_total,
            "benevoles_assigned": len(assigned),
            "positions_total":    total,
            "positions_filled":   filled,
            "fill_rate_pct":      round(filled / total * 100, 1) if total else 0.0,
            "overloaded_benevoles": len(overloaded),
        }

    def _build_assignments(self, solution: Any) -> list[dict]:
        assignments = []

        postes_sorted = sorted(
            solution.affectations.keys(),
            key=lambda p: (
                p.get_categorie().nom,
                p.get_horaire().get_jour(),
                p.get_horaire().get_borne_inf(),
            ),
        )

        for poste in postes_sorted:
            affectes = solution.affectations[poste]
            assignments.append({
                "poste":     self._encode_poste(poste),
                "capacity":  poste.get_size(),
                "filled":    sum(1 for b in affectes if b is not None),
                "benevoles": [self._encode_benevole(b) for b in affectes if b is not None],
            })

        return assignments

    @staticmethod
    def _encode_poste(poste: Any) -> dict:
        horaire = poste.get_horaire()
        return {
            "name":     poste.get_nom(),
            "category": poste.get_categorie().nom,
            "slot": {
                "day_index":  horaire.get_jour(),
                "start_time": horaire.get_borne_inf(),
                "end_time":   horaire.get_borne_sup(),
            },
        }

    @staticmethod
    def _encode_benevole(benevole: Any) -> dict:
        return {
            "first_name": benevole._prenom,
            "last_name":  benevole._nom,
            "email":      benevole._mail,
        }