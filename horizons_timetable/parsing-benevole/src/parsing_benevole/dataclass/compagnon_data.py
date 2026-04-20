from dataclasses import dataclass, field
 
 
@dataclass(frozen=True)
class CompagnonData:
    """Value Object représentant les données de compagnonnage.
 
    Attributes:
        benevole_name:    Nom complet du bénévole déclarant
        compagnons_names: Liste complète pour le matching (inclut variantes inversées)
        original_names:   Noms tels que saisis dans le fichier (sans variantes)
                          — utilisés uniquement pour les messages de warning
    """
    benevole_name:    str
    compagnons_names: tuple[str, ...] = field(default_factory=tuple)
    original_names:   tuple[str, ...] = field(default_factory=tuple)