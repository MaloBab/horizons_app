import logging
from typing import Callable, Optional
from parsing_benevole.settings.schema_configuration import SchemaConfiguration
from parsing_benevole.settings.constants import DEFAULT_MAX_PREFERENCES
from horizons_core.utils.mapping_utils import MappingUtils

logger = logging.getLogger(__name__)

class PreferenceExtractor:
    """Service dédié à l'extraction des préférences."""
    
    def __init__(
        self,
        schema: SchemaConfiguration,
        max_preferences: int = DEFAULT_MAX_PREFERENCES
    ):
        """Initialise l'extracteur de préférences."""
        self._schema = schema
        self._max_preferences = max_preferences
    
    def extraire(
        self,
        ligne: int,
        get_cell_fn: Callable[[int, str], Optional[str]],
    ) -> tuple[list[str], list[str]]:
        
        """Extrait les préférences de postes d'un bénévole."""
        preferences = []
        warnings = []
        
        for i in range(1, self._max_preferences + 1):
            col_name = self._schema.get_preference_column(i) 
            description = get_cell_fn(ligne, col_name)
            
            if description:
                preference_name = MappingUtils.trouver_preference_dans_description(description)
                if preference_name:
                    preferences.append(preference_name)
        
        if len(preferences) != len(set(preferences)):
                msg = f"Préférences en double détectées"
                logger.warning(msg)
                warnings.append(msg)
                seen = set()
                preferences = [p for p in preferences if not (p in seen or seen.add(p))]
                    
        if len(preferences) == 0:
                msg = f"Aucune préférence de poste déclarée"
                logger.warning(msg)
                warnings.append(msg)
            
        
        return preferences, warnings