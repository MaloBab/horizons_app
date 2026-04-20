import logging
import json
from dataclasses import replace
from typing import Optional

from parsing_poste.settings.poste_config import PosteConfig
from horizons_core.parsing.parse_result import ParseResult
from parsing_poste.poste.jour_detector import JourDetector
from parsing_poste.poste.poste_validator import PosteValidator
from parsing_poste.poste.creneau_parseur import CreneauParser
from parsing_poste.poste.categorie_tracker import CategorieTracker
from horizons_core.ods.sheet_reader import SheetReader
from horizons_core.ods.sheet_navigator import SheetNavigator
from horizons_core.ods.cell_span_detector import CellSpanDetector

from horizons_core.dataclass.creneau import Creneau
from horizons_core.dataclass.categorie import Categorie
from horizons_core.dataclass.poste import Poste
from horizons_core.utils.enums import RecruitmentType
from horizons_core.exceptions.parse_exception import ParseError
from horizons_core.exceptions.error_severity import ErrorSeverity

logger = logging.getLogger(__name__)


class ParseurPoste():
    """Parseur principal de postes avec architecture SOLID.

    PRINCIPES APPLIQUÉS :
    - SRP : Chaque service a UNE responsabilité
    - OCP : Extensible via interfaces (Protocol)
    - LSP : Les implémentations respectent les contrats
    - ISP : Interfaces spécialisées (ICreneauParser, etc.)
    - DIP : Dépend d'abstractions (interfaces), pas d'implémentations

    RÉUTILISATION MAXIMALE :
    - Infrastructure : SheetReader, SheetNavigator, CellSpanDetector
    - Dataclass : Creneau, Poste, Categorie (validation incluse)
    - ParseResult GÉNÉRIQUE : Même structure que pour Benevole

    Example:
        >>> config = PosteConfig(row_max=150)
        >>> parseur = ParseurPoste("postes.ods", config=config)
        >>> results = parseur.parse_all()       # list[ParseResult]
        >>> json_str = parseur.to_json()        # str JSON groupé pour export/API
    """

    def __init__(
        self,
        filepath: str,
        config: Optional[PosteConfig] = None,
        sheet_index: int = 0
    ):
        """Initialise le parseur avec injection de dépendances."""
        self._config = config or PosteConfig()

        self._sheet = SheetReader(filepath, sheet_index=sheet_index)
        self._navigator = SheetNavigator(self._sheet)
        self._span_detector = CellSpanDetector(self._sheet)

        self._jour_detector = JourDetector(
            self._sheet,
            self._config,
            self._span_detector
        )
        self._validator = PosteValidator(self._sheet, self._config)
        self._creneau_parser = CreneauParser(
            self._sheet,
            self._config,
            self._span_detector,
            self._jour_detector
        )
        self._categorie_tracker = CategorieTracker()

        logger.info(f"Parseur initialisé pour {filepath}")

    # ========================================================================
    # API PUBLIQUE
    # ========================================================================

    def parse_all(self) -> list[ParseResult]:
        """Parse toutes les lignes et retourne la liste brute de ParseResult.

        Returns:
            list[ParseResult[Poste]] — un résultat par créneau trouvé.
        """
        raw_results: list[ParseResult] = []

        for row in range(self._config.row_debut_postes, self._config.row_max):
            try:
                if self._navigator.is_row_empty(row):
                    continue

                nom_cell         = self._sheet.get_value(row, self._config.col_nom_poste)
                responsible_cell = self._sheet.get_value(row, self._config.col_nom_responsible)

                if not nom_cell or not nom_cell.strip():
                    continue

                self._categorie_tracker.update_if_pole(nom_cell)

                if responsible_cell and responsible_cell.strip():
                    self._categorie_tracker.update_responsible(responsible_cell)

                results_ligne = self._parse_poste_ligne(row)
                raw_results.extend(results_ligne)

            except Exception as e:
                logger.error(f"Erreur ligne {row}: {e}", exc_info=True)
                raw_results.append(ParseResult(
                    entity=None,
                    ligne=row + 1,
                    errors=[ParseError(
                        ligne=row + 1,
                        colonne='general',
                        message=f"Erreur critique: {str(e)}",
                        severity=ErrorSeverity.CRITICAL,
                        exception=e
                    )]
                ))

        valides = sum(1 for r in raw_results if r.is_valid)
        logger.info(f"{valides}/{len(raw_results)} postes valides extraits")

        return raw_results

    # ========================================================================
    # MÉTHODES PRIVÉES
    # ========================================================================

    def _parse_poste_ligne(self, row: int) -> list[ParseResult]:
        """Parse une ligne de poste.

        ⚠️ IMPORTANT : Une ligne peut générer PLUSIEURS postes (un par créneau)

        Returns:
            Liste de ParseResult[Poste] (un par créneau trouvé)
        """
        results = []
        errors  = []

        # 1. Valider que c'est un poste
        if not self._validator.is_valid_poste(row):
            return []

        try:
            # 2. Extraire le nom du poste
            nom_poste = self._sheet.get_value(row, self._config.col_nom_poste)

            if not nom_poste or not nom_poste.strip():
                return []

            # 3. Snapshot de la catégorie courante — chaque poste reçoit sa propre
            #    copie pour que les mises à jour ultérieures du tracker ne l'affectent pas
            current = self._categorie_tracker.get_current_category()

            if not current:
                errors.append(ParseError(
                    ligne=row + 1,
                    colonne='categorie',
                    message="Catégorie/pôle manquante",
                    severity=ErrorSeverity.WARNING
                ))
                cat_obj = Categorie(nom="Inconnu", pole_id=0)
            else:
                cat_obj = replace(current)  # copie immutable du snapshot courant

            # 4. Récupérer le type de recrutement
            type_poste = self._sheet.get_value(row, self._config.col_type_poste)
            if type_poste:
                if "normal" in type_poste.lower():
                    recruitment_type = RecruitmentType.NORMAL
                else:
                    recruitment_type = RecruitmentType.SPECIALISE
            else:
                raise ValueError("Pas de type de poste sur cette ligne.")

            # 5. Parser les créneaux
            creneaux = self._creneau_parser.parse_creneaux_ligne(row)

            if not creneaux:
                result = ParseResult(entity=None, ligne=row + 1)
                for error in errors:
                    result.add_diagnostic(error)
                result.add_diagnostic(ParseError(
                    ligne=row + 1,
                    colonne='creneaux',
                    message=f"Aucun créneau trouvé pour le poste {nom_poste}",
                    severity=ErrorSeverity.WARNING
                ))
                return [result]

            # 6. Pour chaque créneau, créer un Poste
            for creneau in creneaux:
                result_errors = errors.copy()
                col_concerned = self._calculer_colonne_nb_postes(creneau)
                nb_postes_str = self._sheet.get_value(row, col_concerned)

                if not nb_postes_str or not nb_postes_str.strip():
                    result = ParseResult(entity=None, ligne=row +1)
                    for error in result_errors:
                        result.add_diagnostic(error)
                    result.add_diagnostic(ParseError(
                        ligne=row + 1,
                        colonne=f'col_{col_concerned}',
                        message=f"Nombre de postes manquant pour {creneau}",
                        severity=ErrorSeverity.WARNING
                    ))
                    results.append(result)
                    continue

                try:
                    nb_postes = int(nb_postes_str.strip())

                    if nb_postes <= 0:
                        result_errors.append(ParseError(
                            ligne=row + 1,
                            colonne=f'col_{col_concerned}',
                            message=f"Nombre de postes invalide pour {creneau}: {nb_postes_str}",
                            severity=ErrorSeverity.ERROR
                        ))
                        results.append(ParseResult(entity=None, ligne=row + 1, errors=result_errors))
                        continue

                    poste = Poste(
                        nom=nom_poste,
                        categorie=cat_obj,
                        type_benevole=recruitment_type,
                        horaire=creneau,
                        size=nb_postes,
                        responsible=self._categorie_tracker.get_current_responsible()
                    )

                    results.append(ParseResult(
                        entity=poste,
                        ligne=row +1,
                        errors=result_errors
                    ))

                except ValueError as e:
                    result_errors.append(ParseError(
                        ligne=row + 1,
                        colonne=f'col_{col_concerned}',
                        message=f"Nombre de postes invalide: {nb_postes_str}",
                        severity=ErrorSeverity.ERROR,
                        exception=e
                    ))
                    results.append(ParseResult(entity=None, ligne=row + 1, errors=result_errors))

            return results

        except Exception as e:
            logger.error(f"Erreur parsing poste ligne {row}: {e}", exc_info=True)
            errors.append(ParseError(
                ligne=row + 1,
                colonne='general',
                message=f"Erreur: {str(e)}",
                severity=ErrorSeverity.CRITICAL,
                exception=e
            ))
            return [ParseResult(entity=None, ligne=row + 1, errors=errors)]

    def _calculer_colonne_nb_postes(self, creneau: Creneau) -> int:
        """Calcule l'index de colonne contenant le nombre de postes pour un créneau.

        Formule :
        col = col_offset + ((jour - 4) * self._config.creneaux_par_jour + heure - jour - 3)
        """
        jour  = creneau.get_jour()
        heure = creneau.get_borne_inf()

        return (
           self._config.col_offset_debut_creneaux + ((jour - 4) * self._config.creneaux_par_jour + heure - jour - 3)
        )