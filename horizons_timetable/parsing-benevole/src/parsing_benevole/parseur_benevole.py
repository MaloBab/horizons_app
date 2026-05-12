import json
import re
from typing import Optional
import logging

from horizons_core.ods.sheet_reader import SheetReader
from horizons_core.ods.sheet_navigator import SheetNavigator
from horizons_core.ods.column_indexer import ColumnIndexer

from parsing_benevole.settings.schema_configuration import SchemaConfiguration
from parsing_benevole.settings.constants import DEFAULT_HEADER_ROW, DEFAULT_MAX_EMPTY_ROWS

from parsing_benevole.benevole.disponibilite_generator import DisponibiliteGenerator
from parsing_benevole.interfaces.interfaces import IDisponibiliteGenerator, IPreferenceExtractor, ICompagnonMatcher
from parsing_benevole.benevole.compagnon_matcher import CompagnonMatcher, MateWarning
from parsing_benevole.dataclass.compagnon_data import CompagnonData
from parsing_benevole.benevole.preference_extractor import PreferenceExtractor
from parsing_benevole.benevole.column_helper import ColumnHelper

from horizons_core.parsing.parse_result import ParseResult
from horizons_core.utils.text_utils import TextUtils

from horizons_core.dataclass.benevole import Benevole
from horizons_core.dataclass.creneau import Creneau

from horizons_core.exceptions.parse_exception import ParseError
from horizons_core.exceptions.error_severity import ErrorSeverity
from horizons_core.utils.enums import RecruitmentType
from horizons_core.exceptions.invalid_timeslot_exception import InvalidTimeslotException


logger = logging.getLogger(__name__)

# Seuil minimum de créneaux pour qu'une disponibilité soit considérée valide
SEUIL_CRENEAUX_MIN = 5


class ParseurBenevole:
    """Parseur de fichiers ODS contenant les inscriptions des bénévoles."""

    def __init__(
        self,
        filepath: str,
        schema: Optional[SchemaConfiguration] = None,
        disponibilite_generator: Optional[IDisponibiliteGenerator] = None,
        compagnon_matcher: Optional[ICompagnonMatcher] = None,
        preference_extractor: Optional[IPreferenceExtractor] = None,
        header_row: int = DEFAULT_HEADER_ROW,
        max_empty_rows: int = DEFAULT_MAX_EMPTY_ROWS):
        
        self._schema         = schema or SchemaConfiguration()
        self._max_empty_rows = max_empty_rows

        self._sheet     = SheetReader(filepath, sheet_index=0)
        self._navigator = SheetNavigator(self._sheet)
        self._indexer   = ColumnIndexer(
            self._sheet,
            header_row=header_row,
            text_normalizer=TextUtils.nettoyer_texte,
        )

        self._disponibilite_generator = disponibilite_generator or DisponibiliteGenerator()

        self._compagnon_matcher: ICompagnonMatcher = (
            compagnon_matcher if compagnon_matcher is not None else CompagnonMatcher()
        )
        self._preference_extractor = preference_extractor or PreferenceExtractor(self._schema)
        self._column_helper        = ColumnHelper(self._schema, self._indexer)

        logger.info(f"Parseur initialisé pour {filepath}")

    # =========================================================================
    # API PUBLIQUE
    # =========================================================================

    def parse_all(self) -> list[ParseResult]:
        """Parse tout le fichier et retourne la liste brute de ParseResult.

        Returns:
            list[ParseResult[Benevole]]
        """
        results = self._extraire_benevoles()

        benevoles_valides: list[Benevole] = [
            r.entity for r in results if r.is_valid and r.entity is not None
        ]

        if benevoles_valides:
            compagnons_data = self._extraire_compagnons_data(results)
            mate_warnings   = self._compagnon_matcher.associer_compagnons(
                benevoles_valides, compagnons_data
            )
            self._attacher_mate_warnings(results, mate_warnings)

        valides = len(benevoles_valides)
        logger.info(f"{valides}/{len(results)} bénévoles valides extraits")

        return results

    def parse_line(self, ligne: int, seen_emails: set[str]) -> ParseResult:
        """Parse une ligne et retourne un ParseResult.

        Args:
            seen_emails: set des emails déjà rencontrés — permet la détection de doublons.
        """
        result = ParseResult(entity=None, ligne=ligne)

        try:
            nom    = self._extraire_champ(ligne, 'nom',    result, required=True)
            prenom = self._extraire_champ(ligne, 'prenom', result, required=True)

            if not nom or not prenom:
                result.add_diagnostic(ParseError(
                    ligne=ligne,
                    colonne='nom/prenom',
                    message="Nom et prénom sont obligatoires",
                    severity=ErrorSeverity.CRITICAL,
                ))
                return result

            logger.debug(f"Parse ligne {ligne}: {nom} {prenom}")

            email     = self._extraire_champ(ligne, 'email',     result)
            telephone = self._extraire_champ(ligne, 'telephone', result)
            adresse   = self._extraire_champ(ligne, 'adresse',   result)

            # ── Validation email ──────────────────────────────────────────────
            if not email:
                result.add_diagnostic(ParseError(
                    ligne=ligne,
                    colonne='email',
                    message="Email manquant — les affinités par email ne pourront pas être résolues",
                    severity=ErrorSeverity.WARNING,
                ))
            else:
                email_lower = email.lower().strip()

                # Doublon d'email dans le fichier
                if email_lower in seen_emails:
                    result.add_diagnostic(ParseError(
                        ligne=ligne,
                        colonne='email',
                        message=(f"Email '{email}' déjà présent dans le fichier"),
                        severity=ErrorSeverity.WARNING,
                    ))
                else:
                    seen_emails.add(email_lower)

                # Format invalide (pas de @ ou pas de .)
                if not TextUtils.is_valid_email(email):
                    result.add_diagnostic(ParseError(
                        ligne=ligne,
                        colonne='email',
                        message=(
                            f"Email '{email}' invalide (format incorrect) — "
                            f"vérifier la saisie"
                        ),
                        severity=ErrorSeverity.WARNING,
                    ))

            # ── Validation téléphone ──────────────────────────────────────────
            if not telephone:
                result.add_diagnostic(ParseError(
                    ligne=ligne,
                    colonne='telephone',
                    message="Numéro de téléphone manquant",
                    severity=ErrorSeverity.WARNING,
                ))
            else:
                digits_only = re.sub(r'\D', '', telephone)
                if len(digits_only) < 8:
                    result.add_diagnostic(ParseError(
                        ligne=ligne,
                        colonne='telephone',
                        message=(
                            f"Numéro de téléphone suspect '{telephone}' "
                            f"({len(digits_only)} chiffres) — moins de 8 chiffres"
                        ),
                        severity=ErrorSeverity.WARNING,
                    ))

            # ── Validation adresse ────────────────────────────────────────────
            if not adresse:
                result.add_diagnostic(ParseError(
                    ligne=ligne,
                    colonne='adresse',
                    message="Adresse manquante",
                    severity=ErrorSeverity.WARNING,
                ))

            # ── Disponibilités ────────────────────────────────────────────────
            disponibilites = self._extraire_disponibilites(ligne, result)

            # ── Préférences ───────────────────────────────────────────────────
            preferences, preference_warnings = self._preference_extractor.extraire(
                ligne, lambda l, col: self._get_cell_safe(l, col)
            )

            for msg in preference_warnings:
                result.add_diagnostic(ParseError(
                    ligne=ligne,
                    colonne='preferences',
                    message=msg,
                    severity=ErrorSeverity.WARNING,
                ))

            # ── Type bénévole ─────────────────────────────────────────────────
            benevole_specialise = self._extraire_champ(
                ligne, 'type_benevole', result, required=True
            )
            if "oui" in (benevole_specialise or "").lower():
                type_benevole = RecruitmentType.SPECIALISE
            else:
                type_benevole = RecruitmentType.NORMAL

            benevole = Benevole(
                nom=nom,
                prenom=prenom,
                mail=email or "",
                adresse=adresse or "",
                numero_tel=telephone or "",
                disponibilites=disponibilites,
                preferences=preferences,
                type_benevole=type_benevole,
            )

            result.entity = benevole

        except Exception as e:
            logger.error(f"Erreur critique ligne {ligne}: {e}", exc_info=True)
            result.add_diagnostic(ParseError(
                ligne=ligne,
                colonne='general',
                message=f"Erreur critique: {str(e)}",
                severity=ErrorSeverity.CRITICAL,
                exception=e,
            ))

        return result

    # =========================================================================
    # MÉTHODES PRIVÉES
    # =========================================================================

    def _extraire_benevoles(self) -> list[ParseResult]:
        results: list[ParseResult] = []
        ligne = 1
        lignes_vides_consecutives = 0
        seen_emails: set[str] = set()

        while (ligne < self._sheet.get_row_count()
               and lignes_vides_consecutives < self._max_empty_rows):
            try:
                if self._navigator.is_row_empty(ligne):
                    lignes_vides_consecutives += 1
                    ligne += 1
                    continue

                lignes_vides_consecutives = 0

                if self._est_benevole_festival(ligne):
                    result = self.parse_line(ligne, seen_emails)
                    results.append(result)
                    if result.is_valid and result.entity is not None:
                        logger.debug(f"Bénévole ajouté: {result.entity.get_name()}")

                ligne += 1

            except Exception as e:
                logger.error(f"Erreur inattendue ligne {ligne}: {e}", exc_info=True)
                result = ParseResult(entity=None, ligne=ligne)
                result.add_diagnostic(ParseError(
                    ligne=ligne,
                    colonne='general',
                    message=f"Erreur inattendue: {str(e)}",
                    severity=ErrorSeverity.CRITICAL,
                    exception=e,
                ))
                results.append(result)
                ligne += 1

        return results

    def _extraire_compagnons_data(self, results: list[ParseResult]) -> list[CompagnonData]:
        compagnons_data = []
        for result in results:
            if not result.is_valid or result.entity is None:
                continue
            benevole       = result.entity
            compagnons_str = self._get_cell_safe(result.ligne, 'compagnons')
            if compagnons_str:
                compagnons_names = self._compagnon_matcher.extraire_noms_compagnons(compagnons_str)
                original_names   = self._compagnon_matcher.extraire_noms_originaux(compagnons_str)
                logger.debug(
                    f"[compagnons] {benevole.get_name()} | "
                    f"originaux={original_names} | variantes={compagnons_names}"
                )
                if compagnons_names:
                    compagnons_data.append(CompagnonData(
                        benevole_name=benevole.get_name(),
                        compagnons_names=compagnons_names,
                        original_names=original_names,
                    ))
        logger.info(f"{len(compagnons_data)} bénévoles ont des compagnons déclarés")
        return compagnons_data

    def _attacher_mate_warnings(
        self,
        results: list[ParseResult],
        mate_warnings: list[MateWarning],
    ) -> None:
        name_to_result: dict[str, ParseResult] = {}
        for result in results:
            if result.entity is not None:
                name_to_result[result.entity.get_name()] = result

        for mw in mate_warnings:
            pr = name_to_result.get(mw.benevole_name)
            if pr:
                pr.add_diagnostic(ParseError(
                    ligne=pr.ligne,
                    colonne='compagnons',
                    message=mw.message,
                    severity=ErrorSeverity.WARNING,
                ))
            else:
                logger.warning(
                    f"Warning mate non rattachable ('{mw.benevole_name}') : {mw.message}"
                )

    def _get_cell_safe(self, ligne: int, cle_colonne: str) -> Optional[str]:
        try:
            col_index = self._column_helper.get_column_index(cle_colonne)
            return self._sheet.get_value(ligne, col_index)
        except KeyError:
            return None

    def _extraire_champ(
        self,
        ligne: int,
        cle_colonne: str,
        result: ParseResult,
        required: bool = False,
    ) -> Optional[str]:
        try:
            col_index = self._column_helper.get_column_index(cle_colonne)
            value     = self._sheet.get_value(ligne, col_index)
            if value:
                return TextUtils.nettoyer_texte(value)
            if required:
                result.add_diagnostic(ParseError(
                    ligne=ligne,
                    colonne=cle_colonne,
                    message=f"Champ obligatoire '{cle_colonne}' manquant",
                    severity=ErrorSeverity.ERROR,
                ))
            return None
        except KeyError as e:
            result.add_diagnostic(ParseError(
                ligne=ligne,
                colonne=cle_colonne,
                message=f"Colonne '{cle_colonne}' introuvable dans le fichier",
                severity=ErrorSeverity.ERROR,
                exception=e,
            ))
            return None
        except Exception as e:
            result.add_diagnostic(ParseError(
                ligne=ligne,
                colonne=cle_colonne,
                message=f"Erreur extraction champ '{cle_colonne}': {str(e)}",
                severity=ErrorSeverity.WARNING,
                exception=e,
            ))
            return None

    def _extraire_disponibilites(
        self, ligne: int, result: ParseResult
    ) -> list[Creneau]:
        try:
            jour_debut  = self._extraire_champ(ligne, 'jour_debut',  result, required=True)
            heure_debut = self._extraire_champ(ligne, 'heure_debut', result, required=True)
            jour_fin    = self._extraire_champ(ligne, 'jour_fin',    result, required=True)
            heure_fin   = self._extraire_champ(ligne, 'heure_fin',   result, required=True)
            indispos    = self._get_cell_safe(ligne, 'indispos')

            if  not jour_debut or not jour_fin or not heure_debut or not heure_fin:
                result.add_diagnostic(ParseError(
                    ligne=ligne,
                    colonne='disponibilites',
                    message="Dates de disponibilité incomplètes — bénévole ignoré",
                    severity=ErrorSeverity.ERROR,
                ))
                return []

            disponibilites, slot_warnings = self._disponibilite_generator.generer(
                jour_debut, heure_debut, jour_fin, heure_fin, indispos
            )

            for msg in slot_warnings:
                result.add_diagnostic(ParseError(
                    ligne=ligne,
                    colonne='disponibilites',
                    message=msg,
                    severity=ErrorSeverity.WARNING,
                ))

            if not disponibilites and not slot_warnings:
                result.add_diagnostic(ParseError(
                    ligne=ligne,
                    colonne='disponibilites',
                    message=(
                        f"Aucun créneau généré pour la plage "
                        f"{jour_debut} {heure_debut} → {jour_fin} {heure_fin}"
                    ),
                    severity=ErrorSeverity.WARNING,
                ))
            elif 0 < len(disponibilites) < SEUIL_CRENEAUX_MIN:
                result.add_diagnostic(ParseError(
                    ligne=ligne,
                    colonne='disponibilites',
                    message=(
                        f"Seulement {len(disponibilites)} créneau(x) généré(s) "
                        f"({jour_debut} {heure_debut} → {jour_fin} {heure_fin}) — "
                        f"vérifier les dates (seuil minimum : {SEUIL_CRENEAUX_MIN} créneaux)"
                    ),
                    severity=ErrorSeverity.WARNING,
                ))

            return disponibilites

        except InvalidTimeslotException as e:
            result.add_diagnostic(ParseError(
                ligne=ligne, colonne='disponibilites',
                message=f"Créneau invalide : {str(e)}",
                severity=ErrorSeverity.ERROR, exception=e,
            ))
            return []
        except ValueError as e:
            result.add_diagnostic(ParseError(
                ligne=ligne, colonne='disponibilites',
                message=f"Valeur invalide dans les disponibilités : {str(e)}",
                severity=ErrorSeverity.ERROR, exception=e,
            ))
            return []
        except Exception as e:
            result.add_diagnostic(ParseError(
                ligne=ligne, colonne='disponibilites',
                message=f"Erreur inattendue lors de l'extraction des disponibilités : {str(e)}",
                severity=ErrorSeverity.ERROR, exception=e,
            ))
            return []

    def _est_benevole_festival(self, ligne: int) -> bool:
        try:
            intervalle      = self._get_cell_safe(ligne, 'intervalle')
            autres_missions = self._get_cell_safe(ligne, 'autres_missions')
            if intervalle and 'pendant' in TextUtils.nettoyer_texte(intervalle):
                return True
            if autres_missions and 'oui' in TextUtils.nettoyer_texte(autres_missions):
                return True
            return False
        except Exception as e:
            logger.warning(f"Erreur vérification bénévole festival ligne {ligne}: {e}")
            return False
        
def main():
    parseur = ParseurBenevole("C:\\Users\\Malo Babinot\\Desktop\\Programmation\\Horizons Open Sea Festival\\documents & utils\\Inscriptions Bénévoles Horizons 2026 (réponses).ods")
    parseur.parse_all()
    
if __name__ == "__main__":
    main()