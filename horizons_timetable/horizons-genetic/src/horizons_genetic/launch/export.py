"""
Etape 6 — Export de la solution (ODS et/ou JSON).

Ce module ne contient que le routage entre les exporteurs ;
chaque format est isolé dans sa propre fonction.
"""
import json
import logging
from pathlib import Path
from typing import Any

from horizons_genetic.launch.config import ExportFormat
from horizons_genetic.launch.solution_encoder import SolutionJSONEncoder

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Point d'entrée public
# ---------------------------------------------------------------------------

def export_solution(
    solution: Any,
    benevoles: list[Any],
    fmt: ExportFormat,
    fichier_ods:  Path,
    fichier_json: Path,
) -> None:
    """Exporte la solution dans le(s) format(s) demandé(s).

    N'arrête jamais le pipeline : un export raté est loggué mais ne masque
    pas une solution valide déjà calculée.

    Args:
        solution:     Chromosome validé.
        benevoles:    Liste complète des bénévoles (pour les statistiques JSON).
        fmt:          Format d'export (ODS, JSON ou BOTH).
        fichier_ods:  Chemin de destination ODS.
        fichier_json: Chemin de destination JSON.
    """
    logger.info("")
    logger.info("=" * 60)
    logger.info("ÉTAPE 6 — EXPORT")
    logger.info("=" * 60)

    if fmt in (ExportFormat.ODS, ExportFormat.BOTH):
        _export_ods(solution, fichier_ods)

    if fmt in (ExportFormat.JSON, ExportFormat.BOTH):
        _export_json(solution, benevoles, fichier_json)


# ---------------------------------------------------------------------------
# Exporteurs privés
# ---------------------------------------------------------------------------

def _export_ods(solution: Any, fichier: Path) -> None:
    """Exporte la solution au format ODS via ODSExporter."""
    from horizons_genetic.output.ods_exporter import ODSExporter

    logger.info(f"[ODS]  Destination : {fichier}")
    try:
        ODSExporter().export(solution, str(fichier))
        logger.info(f"[ODS]  ✅ Export réussi : {fichier}")
    except Exception:
        logger.error("[ODS]  ❌ Échec de l'export ODS.", exc_info=True)


def _export_json(solution: Any, benevoles: list[Any], fichier: Path) -> None:
    """Exporte la solution au format JSON via SolutionJSONEncoder."""

    logger.info(f"[JSON] Destination : {fichier}")
    try:
        encoder  = SolutionJSONEncoder(indent=2, ensure_ascii=False)
        payload  = encoder.encode_solution(solution, benevoles_total=len(benevoles))
        fichier.parent.mkdir(parents=True, exist_ok=True)
        fichier.write_text(
            json.dumps(payload, cls=SolutionJSONEncoder, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        logger.info(f"[JSON] ✅ Export réussi : {fichier}")
    except Exception:
        logger.error("[JSON] ❌ Échec de l'export JSON.", exc_info=True)