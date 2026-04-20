"""Aide à la navigation dans une feuille de calcul."""

import logging
from horizons_core.ods.isheet_reader import ISheetReader

logger = logging.getLogger(__name__)


class SheetNavigator:
    """
    Aide à la navigation dans une feuille de calcul.
    Fournit des méthodes utilitaires pour parcourir les données.
    """
    
    def __init__(self, sheet: ISheetReader):
        """
        Initialise le navigateur.
        
        Args:
            sheet: Lecteur de feuille
        """
        self._sheet = sheet
    
    def _validate_row(self, row: int) -> None:
        """Valide un index de ligne."""
        if row < 0:
            raise ValueError(f"Index de ligne négatif : {row}")
        if row >= self._sheet.get_row_count():
            raise ValueError(
                f"Index de ligne hors limites : {row} "
                f"(max: {self._sheet.get_row_count() - 1})"
            )
    
    
    def is_row_empty(self, row: int) -> bool:
        """
        Vérifie si une ligne est entièrement vide.
        
        Args:
            row: Numéro de ligne
            
        Returns:
            True si la ligne est vide, False sinon
            
        Raises:
            ValueError: Si l'index de ligne est invalide
        """
        self._validate_row(row)
        
        for col in range(self._sheet.get_column_count()):
            try:
                if self._sheet.get_value(row, col):
                    return False
            except IndexError:
                logger.debug("IndexError ignorée sur (row=%d, col=%d)", row, col)
                continue
        
        return True
    