from dataclasses import dataclass
from typing import Optional
from horizons_core.exceptions.error_severity import ErrorSeverity


@dataclass
class ParseError:
    """Représente une erreur de parsing.
    
    Attributes:
        ligne: Numéro de ligne
        colonne: Nom de la colonne
        message: Message d'erreur
        severity: Niveau de sévérité
        exception: Exception originale (optionnel)
    """
    ligne: int
    colonne: str
    message: str
    severity: ErrorSeverity = ErrorSeverity.ERROR
    exception: Optional[Exception] = None
    
    def __str__(self) -> str:
        return f"[{self.severity.value.upper()}] Ligne {self.ligne}, colonne '{self.colonne}': {self.message}"