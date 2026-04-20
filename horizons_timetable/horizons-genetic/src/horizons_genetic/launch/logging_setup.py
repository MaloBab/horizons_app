"""
Configuration du système de logging pour le pipeline Horizons.
"""
import logging
import sys
from pathlib import Path


def setup_logging(log_file: Path, level: int = logging.INFO) -> logging.Logger:
    """Configure et retourne le logger racine du pipeline.

    Args:
        log_file: Chemin vers le fichier de log.
        level:    Niveau de log (défaut : INFO).

    Returns:
        Logger configuré avec handlers console et fichier.
    """
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    formatter = logging.Formatter(fmt)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    return logging.getLogger(__name__)