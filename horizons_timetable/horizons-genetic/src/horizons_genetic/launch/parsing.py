"""
Etapes de parsing du pipeline Horizons.

Les parseurs retournent des objets ParseResult sérialisables en JSON.
Ce module extrait les entités domaine valides et centralise le rapport d'erreurs.
"""
import logging
import sys
from pathlib import Path
from typing import Any

from horizons_core.parsing.parse_result import ParseResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Types locaux
# ---------------------------------------------------------------------------

ParseResults  = list[ParseResult]   # list[ParseResult]
DomainObjects = list[Any]


# ---------------------------------------------------------------------------
# Helpers privés
# ---------------------------------------------------------------------------

def _log_parse_summary(
    entity_label: str,
    results: ParseResults,
    valid_count: int,
) -> None:
    total    = len(results)
    erreurs  = sum(1 for r in results if not r.is_valid)
    warnings = sum(
        1 for r in results
        for e in r.errors
        if e.severity.name == "WARNING"
    )

    logger.info(f"✅ {valid_count} {entity_label} valide(s) / {total} lignes")
    if erreurs:
        logger.warning(f"⚠️  {erreurs} ligne(s) invalide(s)")
    if warnings:
        logger.warning(f"⚠️  {warnings} warning(s)")


def _extract_valid_entities(results: ParseResults) -> DomainObjects:
    """Extrait les entités valides d'une liste de ParseResult."""
    return [r.entity for r in results if r.is_valid and r.entity is not None]


def _abort_if_empty(entities: DomainObjects, label: str) -> None:
    if not entities:
        logger.critical(f"Aucun·e {label} valide trouvé·e — arrêt du pipeline.")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Etapes publiques
# ---------------------------------------------------------------------------

def parse_postes(fichier: Path, row_max: int) -> DomainObjects:
    """Etape 1 — Parse les postes depuis le fichier ODS."""
    from parsing_poste.parseur_poste import ParseurPoste
    from parsing_poste.settings.poste_config import PosteConfig

    logger.info("=" * 60)
    logger.info("ÉTAPE 1 — PARSING DES POSTES")
    logger.info("=" * 60)
    logger.info(f"Fichier : {fichier}")

    try:
        config  = PosteConfig(row_max=row_max)
        parseur = ParseurPoste(str(fichier), config=config)
        results: ParseResults = parseur.parse_all()
    except Exception:
        logger.critical("Échec du parsing postes.", exc_info=True)
        sys.exit(1)

    postes = _extract_valid_entities(results)
    _log_parse_summary("poste(s)", results, len(postes))
    _abort_if_empty(postes, "poste")

    return postes


def parse_benevoles(fichier: Path) -> DomainObjects:
    """Etape 2 — Parse les bénévoles depuis le fichier ODS."""
    from parsing_benevole.parseur_benevole import ParseurBenevole
    from parsing_benevole.settings.schema_configuration import SchemaConfiguration

    logger.info("")
    logger.info("=" * 60)
    logger.info("ÉTAPE 2 — PARSING DES BÉNÉVOLES")
    logger.info("=" * 60)
    logger.info(f"Fichier : {fichier}")

    try:
        schema  = SchemaConfiguration()
        parseur = ParseurBenevole(str(fichier), schema=schema)
        results: ParseResults = parseur.parse_all()
    except Exception:
        logger.critical("Échec du parsing bénévoles.", exc_info=True)
        sys.exit(1)

    benevoles = _extract_valid_entities(results)
    _log_parse_summary("bénévole(s)", results, len(benevoles))
    _abort_if_empty(benevoles, "bénévole")

    return benevoles