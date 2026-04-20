"""Interfaces (Protocols) du module parsing_benevole.

Toutes les dépendances de ce module doivent être soit :
- des types du domaine (``horizons_core``) ;
- des value objects sans dépendance ascendante (ex: ``MateWarning``).

On n'importe jamais ici une classe concrète de ``parsing_benevole.benevole.*``
pour éviter les cycles d'import.
"""

from __future__ import annotations

from typing import Callable, Optional, Protocol

from horizons_core.dataclass.benevole import Benevole
from horizons_core.dataclass.creneau import Creneau
from parsing_benevole.dataclass.compagnon_data import CompagnonData
from parsing_benevole.dataclass.mate_warning import MateWarning


class IDisponibiliteGenerator(Protocol):
    """Interface pour la génération de disponibilités."""

    def generer(
        self,
        jour_debut: str,
        heure_debut: str,
        jour_fin: str,
        heure_fin: str,
        indispos: Optional[str],
    ) -> tuple[list[Creneau], list[str]]:
        """Génère les créneaux de disponibilité.

        Returns:
            tuple (créneaux valides, liste de messages de warning).
        """
        ...


class ICompagnonMatcher(Protocol):
    """Interface pour le matching de compagnons."""

    def construire_index(self, benevoles: list[Benevole]) -> None:
        """Construit l'index des bénévoles pour recherche rapide."""
        ...

    def associer_compagnons(
        self,
        benevoles: list[Benevole],
        compagnons_data: list[CompagnonData],
    ) -> list[MateWarning]:
        """Associe les compagnons entre bénévoles.

        Returns:
            Liste de :class:`MateWarning` pour les compagnons non trouvés.
        """
        ...

    def extraire_noms_compagnons(
        self, liste_compagnons: Optional[str]
    ) -> tuple[str, ...]:
        """Extrait les noms et génère les variantes inversées pour le matching.

        Note:
            Retourne la liste complète (originaux + variantes inversées)
            destinée à ``CompagnonData.compagnons_names``.
            Les noms originaux seuls doivent alimenter
            ``CompagnonData.original_names``.
        """
        ...

    def extraire_noms_originaux(
        self, liste_compagnons: Optional[str]
    ) -> tuple[str, ...]:
        """Extrait uniquement les noms originaux (sans variantes inversées).

        À utiliser pour ``CompagnonData.original_names``.
        """
        ...


class IPreferenceExtractor(Protocol):
    """Interface pour l'extraction des préférences."""

    def extraire(
        self,
        ligne: int,
        get_cell_fn: Callable[[int, str], Optional[str]],
    ) -> tuple[list[str], list[str]]:
        """Extrait les préférences de postes.

        Returns:
            tuple (liste de préférences, liste de messages de warning).
        """
        ...
