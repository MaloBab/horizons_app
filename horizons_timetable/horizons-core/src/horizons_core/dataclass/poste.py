from horizons_core.dataclass.categorie import Categorie
from horizons_core.dataclass.creneau import Creneau
from typing import Optional

from horizons_core.utils.enums import RecruitmentType

class Poste:
    """Poste à pourvoir.""" 
 
    def __init__(
        self,
        nom:           str,
        categorie:     Categorie,
        type_benevole: RecruitmentType,
        horaire:       Creneau,
        size:          int,
        responsible:   Optional[str] = None,
    ):
        self._id          = None 
        self._nom         = nom
        self._categorie   = categorie
        self._type        = type_benevole
        self._horaire     = horaire
        self._size        = size
        self._responsible = responsible

    def get_id(self)       -> Optional[int]:   return self._id
    def get_nom(self)         -> str:             return self._nom
    def get_categorie(self)   -> Categorie:       return self._categorie
    def get_type(self)        -> RecruitmentType: return self._type
    def get_size(self)        -> int:             return self._size
    def get_horaire(self)     -> Creneau:         return self._horaire
    def get_responsible(self) -> Optional[str]:   return self._responsible
    
    def set_id(self, id: int) -> None:
        self._id = id

    def __str__(self) -> str:
        return (
            f"Poste {self._id} - {self._categorie.nom} ({self._categorie.pole_id}) : {self._nom} "
            f"({self._horaire})\n"
            f"Responsable : {self._responsible or '—'}\n"
            f"Bénévole(s) nécessaire(s) : {self._size} - {self._type.value}"
        )