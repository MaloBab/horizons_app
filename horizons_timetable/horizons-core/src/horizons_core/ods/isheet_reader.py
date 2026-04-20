"""Interface pour la lecture de feuilles de calcul."""

from typing import Protocol, Optional


class ISheetReader(Protocol):
    """
    Interface pour la lecture de feuilles de calcul.
    Permet de mocker facilement pour les tests.
    """
    
    def get_value(self, row: int, col: int) -> Optional[str]:
        """
        Récupère la valeur d'une cellule.
        
        Args:
            row: Numéro de ligne (0-indexed)
            col: Numéro de colonne (0-indexed)
            
        Returns:
            Valeur de la cellule ou None
        """
        ...
    
    def get_row_count(self) -> int:
        """Retourne le nombre de lignes."""
        ...
    
    def get_column_count(self) -> int:
        """Retourne le nombre de colonnes."""
        ...
    
    
    def get_merge_info(self, row: int, col: int) -> Optional[dict[str, int]]:
        """
        Récupère les informations de fusion d'une cellule.
        
        Args:
            row: Numéro de ligne
            col: Numéro de colonne
            
        Returns:
            dict avec 'colspan' et 'rowspan' ou None si pas fusionnée
        """
        ...
