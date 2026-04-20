from typing import Optional
from horizons_core.dataclass.categorie import Categorie
from horizons_core.utils.mapping_utils import MappingUtils
from horizons_core.utils.text_utils import TextUtils
from horizons_core.utils.enums import Pole


class CategorieTracker:
    """Suit la catégorie courante lors du parsing ligne par ligne."""

    def __init__(self) -> None:
        self._current:     Optional[Categorie] = None
        self._responsible: Optional[str]       = None  # ← stocké séparément


    def update_if_pole(self, cell_value: str) -> bool:
        normalized = TextUtils.nettoyer_texte(cell_value)
        if normalized.startswith("pole"):
            pole_id = MappingUtils.get_pole_id(normalized)
            self._current = Categorie(nom=cell_value.strip(), pole_id=pole_id)
            return True
        return False
        

    def update_responsible(self, responsable: str) -> None:
        """Met à jour le responsable courant (par ligne, pas par pôle)."""
        if responsable and responsable.strip():
            self._responsible = responsable.strip()

    def get_current_category(self) -> Optional[Categorie]:
        return self._current

    def get_current_responsible(self) -> Optional[str]:
        """Retourne le dernier responsable connu."""
        return self._responsible