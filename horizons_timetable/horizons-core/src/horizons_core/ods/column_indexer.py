"""Indexeur de colonnes avec recherche par mots-clés."""

import logging
from .isheet_reader import ISheetReader
from horizons_core.utils.text_utils import TextUtils


logger = logging.getLogger(__name__)


class ColumnIndexer:
    """
    Indexeur de colonnes générique.
    Permet de retrouver des colonnes par mot-clé dans les en-têtes.
    """
    
    def __init__(
        self,
        sheet_reader: ISheetReader,
        header_row: int = 0,
        text_normalizer=None
    ):
        """
        Initialise l'indexeur.
        
        Args:
            sheet_reader: Lecteur de feuille
            header_row: Numéro de ligne contenant les en-têtes (défaut: 0)
            text_normalizer: Fonction de normalisation de texte (optionnel)
        """
        self._sheet_reader = sheet_reader
        self._header_row = header_row
        self._text_normalizer = text_normalizer or TextUtils.nettoyer_texte
        self._indices: dict[str, int] = {}
        
        self._initialize_indices()
    
    def _initialize_indices(self) -> None:
        self._indices = {
            normalized: col
            for col in range(self._sheet_reader.get_column_count())
            if (header := self._sheet_reader.get_value(self._header_row, col))
            and (normalized := self._text_normalizer(header))
        }
        logger.info("Indexé %d colonnes", len(self._indices))
    
    def get_column_index(self, keyword: str) -> int:
        """
        Trouve l'index de colonne contenant le mot-clé.
        
        Args:
            keyword: Mot-clé à rechercher dans les en-têtes
            
        Returns:
            Index de la colonne
            
        Raises:
            KeyError: Si aucune colonne ne correspond
            
        Example:
            >>> indexer.get_column_index("nom")
            2  # La colonne "Nom" est à l'index 2
        """
        keyword_normalized = self._text_normalizer(keyword)
        
        # Recherche exacte d'abord
        if keyword_normalized in self._indices:
            return self._indices[keyword_normalized]
        
        # Recherche partielle (mot-clé contenu dans l'en-tête)
        for header, index in self._indices.items():
            if keyword_normalized in header:
                return index
        
        raise KeyError(f"Colonne introuvable pour le mot-clé : '{keyword}'")