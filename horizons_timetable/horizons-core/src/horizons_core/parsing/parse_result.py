from dataclasses import dataclass, field
from typing import Optional, TypeVar, Generic
from horizons_core.exceptions.parse_exception import ParseError
from horizons_core.exceptions.error_severity import ErrorSeverity

T = TypeVar('T') 

@dataclass
class ParseResult(Generic[T]):
    """Résultat d'un parsing avec gestion d'erreurs GÉNÉRIQUE.
    
    ✅ RÉUTILISATION : Même structure que ParseResult[Benevole]
    ✅ GÉNÉRIQUE : Fonctionne pour Benevole, Poste, ou tout autre type
    
    Attributes:
        entity: Entité parsée (Benevole, Poste, etc.) - None si erreur critique
        ligne: Numéro de ligne d'origine
        errors: Liste des erreurs rencontrées
        warnings: Liste des avertissements
    """
    entity: Optional[T]
    ligne: int
    errors: list[ParseError] = field(default_factory=list)
    warnings: list[ParseError] = field(default_factory=list)
    
    @property
    def is_valid(self) -> bool:
        """Retourne True si le parsing est valide (pas d'erreur critique)."""
        return self.entity is not None and not any(
            e.severity == ErrorSeverity.CRITICAL for e in self.errors
        )
    
    def add_diagnostic(self, diagnostic: ParseError) -> None:
        if diagnostic.severity == ErrorSeverity.WARNING:
            self.warnings.append(diagnostic)
        else:
            self.errors.append(diagnostic)
