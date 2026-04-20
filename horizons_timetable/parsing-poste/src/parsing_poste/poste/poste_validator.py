import logging
from parsing_poste.settings.poste_config import PosteConfig

from horizons_core.ods.sheet_reader import SheetReader

logger = logging.getLogger(__name__)

class PosteValidator:
    """Valide qu'une ligne contient un poste valide.
    
    RESPONSABILITÉ : Logique de validation des postes
    RÉUTILISE : TextUtils pour normalisation
    """
    
    def __init__(self, sheet: SheetReader, config: PosteConfig):
        """Initialise le validateur."""
        self._sheet = sheet
        self._config = config
    
    def is_valid_poste(self, row: int) -> bool:
        """Vérifie si la ligne contient un poste valide.
        
        Critères :
        1. Colonne nom_poste non vide
        """
        try:
            # 1. Vérifier nom du poste
            nom_poste = self._sheet.get_value(row, self._config.col_nom_poste)
            if not nom_poste or not nom_poste.strip():
                return False
            
            # 2. Vérifier type de poste
            type_poste = self._sheet.get_value(row, self._config.col_type_poste)
            if not type_poste:
                return False
            
            return True
            
        except (IndexError, ValueError) as e:
            logger.debug(f"Erreur validation ligne {row}: {e}")
            return False
