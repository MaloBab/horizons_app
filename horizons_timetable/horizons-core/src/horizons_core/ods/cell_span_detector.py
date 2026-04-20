"""Détecteur de spans de cellules basé sur le SheetReader amélioré."""

from horizons_core.ods.isheet_reader import ISheetReader


class CellSpanDetector:
    """
    Détecte et analyse les fusions de cellules (rowspan/colspan).
    Utilise les informations natives du format ODF.
    """
    
    def __init__(self, sheet: ISheetReader):
        """
        Initialise le détecteur.
        
        Args:
            sheet: Lecteur de feuille
        """
        self._sheet = sheet
    
    def get_colspan(self, row: int, col: int) -> int:
        """
        Récupère le colspan d'une cellule.
        
        Args:
            row: Ligne
            col: Colonne
            
        Returns:
            Nombre de colonnes fusionnées (minimum 1)
            
        Example:
            >>> detector.get_colspan(5, 10)
            3  # La cellule s'étend sur 3 colonnes
        """
        merge_info = self._sheet.get_merge_info(row, col)
        return merge_info['colspan'] if merge_info else 1
    