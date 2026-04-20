"""
Point d'entrée du pipeline Horizons — Affectation bénévoles.

Usage :
    python main.py                    # format défini dans config.py
    python main.py --format ods
    python main.py --format json
    python main.py --format both
"""
import argparse
import logging

from horizons_core.dataclass.benevole import Benevole
from horizons_core.dataclass.poste import Poste
from horizons_core.utils.enums import RecruitmentType
from horizons_genetic.genetic.settings import config as GeneticConfig
from horizons_genetic.launch import config as LaunchConfig
from horizons_genetic.launch.export import export_solution
from horizons_genetic.launch.genetic import run_genetic
from horizons_genetic.launch.logging_setup import setup_logging
from horizons_genetic.launch.parsing import parse_benevoles, parse_postes
from horizons_genetic.launch.statistics import log_statistics

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Horizons — Algorithme d'affectation bénévoles"
    )
    parser.add_argument(
        "--format",
        choices=["ods", "json", "both"],
        default=None,
        help=(
            "Format d'export de la solution. "
            "Surcharge la valeur EXPORT_FORMAT de config.py. "
            "Valeurs : ods | json | both"
        ),
    )
    return parser.parse_args()


def _resolve_export_format(cli_format: str | None) -> LaunchConfig.ExportFormat:
    """Retourne le format effectif : CLI en priorité, sinon config.py."""
    if cli_format is None:
        return LaunchConfig.EXPORT_FORMAT
    return LaunchConfig.ExportFormat[cli_format.upper()]


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def main() -> None:
    args          = _parse_args()
    export_format = _resolve_export_format(args.format)

    setup_logging(LaunchConfig.FICHIER_LOG)

    logger.info("=" * 60)
    logger.info("HORIZONS — ALGORITHME D'AFFECTATION BÉNÉVOLES")
    logger.info(f"Format d'export : {export_format.name}")
    logger.info("=" * 60)

    # Étape 1 & 2 : Parsing
    postes    = parse_postes(LaunchConfig.FICHIER_POSTES, LaunchConfig.POSTE_ROW_MAX)
    postes: list[Poste] = [p for p in postes if p.get_type() == RecruitmentType.NORMAL]
    benevoles: list[Benevole] = parse_benevoles(LaunchConfig.FICHIER_BENEVOLES)
    print(f"Postes normaux parsés : {len(postes)}")

    # Étape 3 : Algorithme génétique
            
    solution, engine = run_genetic(postes, benevoles, GeneticConfig.GeneticConfig())
    
    # Étape 4 : Statistiques
    log_statistics(solution, benevoles, engine)

    # Étape 5 : Export
    export_solution(
        solution      = solution,
        benevoles     = benevoles,
        fmt           = export_format,
        fichier_ods   = LaunchConfig.FICHIER_EXPORT_ODS,
        fichier_json  = LaunchConfig.FICHIER_EXPORT_JSON,
    )

    logger.info("")
    logger.info(
        f"Traitement terminé — consultez {LaunchConfig.FICHIER_LOG} pour les détails."
    )


if __name__ == "__main__":
    main()