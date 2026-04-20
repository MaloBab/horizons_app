
from typing import Protocol
from horizons_core.dataclass.creneau import Creneau


class ICreneauParser(Protocol):
    """Interface pour parser les créneaux d'un poste."""
    
    def parse_creneaux_ligne(self, row: int) -> list[Creneau]:
        """Parse tous les créneaux d'une ligne de poste.
        
        Args:
            row: Numéro de ligne
            
        Returns:
            Liste des créneaux trouvés
        """
        ...


class IJourDetector(Protocol):
    """Interface pour détecter le jour d'un créneau."""
    
    def get_jour_from_column(self, col: int) -> int:
        """Détermine le jour associé à une colonne (via cellules fusionnées).
        
        Args:
            col: Index de colonne
            
        Returns:
            Jour (0-7)
        """
        ...