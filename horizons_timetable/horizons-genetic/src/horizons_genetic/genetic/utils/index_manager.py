"""
Gestionnaire d'indices pour conversion objets <-> IDs.
"""
from typing import Optional
 
from horizons_core.dataclass.poste import Poste
from horizons_core.dataclass.benevole import Benevole
 
 
class IndexManager:
    """
    Gère les conversions bidirectionnelles entre objets domaine et indices entiers.
 
    Utilisé par tous les opérateurs génétiques pour travailler sur des int
    plutôt que sur des objets Python (performance + hashabilité).
    """

 
    def __init__(self):
        self._poste_to_id:    dict[Poste,    int] = {}
        self._id_to_poste:    dict[int,    Poste] = {}
        self._benevole_to_id: dict[Benevole, int] = {}
        self._id_to_benevole: dict[int, Benevole] = {}
        self._initialized = True
 
    def build_indices(self, postes: list[Poste], benevoles: list[Benevole]) -> None:
        """Construit les indices à partir des listes de postes et bénévoles."""
        self._poste_to_id.clear()
        self._id_to_poste.clear()
        for idx, poste in enumerate(postes):
            self._poste_to_id[poste] = idx
            self._id_to_poste[idx]   = poste
 
        self._benevole_to_id.clear()
        self._id_to_benevole.clear()
        for idx, benevole in enumerate(benevoles):
            self._benevole_to_id[benevole] = idx
            self._id_to_benevole[idx]      = benevole
 
    def poste_to_id(self, poste: Poste) -> int:
        return self._poste_to_id[poste]
 
    def id_to_poste(self, poste_id: int) -> Poste:
        return self._id_to_poste[poste_id]
 
    def benevole_to_id(self, benevole: Benevole) -> int:
        return self._benevole_to_id.get(benevole, -1)
 
    def id_to_benevole(self, benevole_id: int) -> Optional[Benevole]:
        return self._id_to_benevole.get(benevole_id)
 
    def get_all_poste_ids(self) -> list[int]:
        return list(self._id_to_poste.keys())
 
    def get_all_benevole_ids(self) -> list[int]:
        return list(self._id_to_benevole.keys())