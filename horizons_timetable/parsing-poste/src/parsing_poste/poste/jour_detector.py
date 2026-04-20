import logging
from typing import Optional

from horizons_core.ods.sheet_reader import SheetReader
from horizons_core.ods.cell_span_detector import CellSpanDetector
from parsing_poste.settings.poste_config import PosteConfig

from horizons_core.utils.date_utils import DateUtils

logger = logging.getLogger(__name__)

class JourDetector:
    """Détecte le jour associé à une colonne via les cellules fusionnées.
    
    RESPONSABILITÉ : Gestion de la logique des jours dans les en-têtes fusionnés
    RÉUTILISE : CellSpanDetector pour détecter les fusions
    """
    
    def __init__(
        self,
        sheet: SheetReader,
        config: PosteConfig,
        span_detector: CellSpanDetector
    ):
        """Initialise le détecteur de jours."""
        self._sheet = sheet
        self._config = config
        self._span_detector = span_detector
        self._cache: dict[int, int] = {}  # Cache col -> jour
    
    def get_jour_from_column(self, col: int) -> int:
        """Détermine le jour d'une colonne en remontant aux cellules fusionnées.
        
        Algorithme :
        1. Partir de la colonne actuelle
        2. Remonter vers la gauche jusqu'à trouver une cellule non vide
        3. Convertir le texte trouvé en jour (0-7)
        """
        # Cache pour éviter recalculs
        if col in self._cache:
            return self._cache[col]

        jour_precedent = None  # ← tracker le dernier jour trouvé

        for col_search in range(col, -1, -1):
            try:
                cell_value = self._sheet.get_value(self._config.row_jours, col_search)

                if cell_value and cell_value.strip():
                    # Chercher le jour précédent pour résoudre Lundi=0 vs Lundi=7
                    jour_avant = self._trouver_jour_precedent(col_search)
                    jour = DateUtils.convertir_jour_en_int(cell_value, jour_precedent=jour_avant)
                    self._cache[col] = jour
                    return jour

            except (ValueError, IndexError) as e:
                logger.debug(f"Erreur détection jour col {col_search}: {e}")
                continue

        logger.warning(f"Jour introuvable pour colonne {col}")
        return -1
    
    def _trouver_jour_precedent(self, col: int) -> Optional[int]:
        """Retourne le jour de la cellule de jour la plus proche à gauche."""
        for col_search in range(col - 1, -1, -1):
            try:
                cell_value = self._sheet.get_value(self._config.row_jours, col_search)
                if cell_value and cell_value.strip():
                    return DateUtils.convertir_jour_en_int(cell_value)
            except (ValueError, IndexError):
                continue
        return None