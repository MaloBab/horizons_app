"""
Configuration globale du pipeline Horizons.
Modifiez uniquement ce fichier pour adapter les chemins et paramètres.
"""
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

# ---------------------------------------------------------------------------
# Format d'export
# ---------------------------------------------------------------------------

class ExportFormat(Enum):
    ODS  = auto()
    JSON = auto()
    BOTH = auto()


# ---------------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------------

FICHIER_POSTES = Path("C:/Users/Malo Babinot/Desktop/Programmation/Horizons Open Sea Festival/documents & utils/Besoins bénévoles 2025.2.ods")


FICHIER_BENEVOLES = Path("C:\\Users\\Malo Babinot\\Desktop\\Programmation\\Horizons Open Sea Festival\\documents & utils\\Inscriptions Récent.ods")

FICHIER_EXPORT_ODS  = Path("C:/Users/Malo Babinot/Desktop/affectation_resultat.ods")
FICHIER_EXPORT_JSON = Path("C:/Users/Malo Babinot/Desktop/affectation_resultat.json")

FICHIER_LOG = Path("horizons_genetic.log")

# Format utilise par defaut (surchargeable via --format en CLI)
EXPORT_FORMAT: ExportFormat = ExportFormat.ODS


# ---------------------------------------------------------------------------
# Parametres de parsing
# ---------------------------------------------------------------------------

POSTE_ROW_MAX: int = 150


# ---------------------------------------------------------------------------
# Seuils metier
# ---------------------------------------------------------------------------

MAX_HEURES_PAR_JOUR:   int = 6
MAX_OVERLOADED_LOGGED: int = 10
MAX_ERRORS_LOGGED:     int = 10