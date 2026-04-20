"""Constantes de parsing pour le module ``parsing_benevole``.

Corrections appliquées par rapport à la version originale :

- La classe ``ParseConstants`` utilisée comme simple namespace de constantes
  est supprimée.  En Python, une classe sans état ni comportement est un
  anti-pattern quand son seul rôle est de regrouper des noms : un module remplit
  ce rôle de manière idiomatique, sans la syntaxe ``ParseConstants.FOO``.
- Les constantes sont désormais des variables de module en ``SCREAMING_SNAKE_CASE``
  (PEP 8 §Constants), directement importables :
  ``from parsing_benevole.settings.constants import DEFAULT_MAX_EMPTY_ROWS``.
- Les types sont annotés explicitement.  Python ≥ 3.11 est requis par le projet,
  les annotations de variables de module sont donc pleinement supportées (PEP 526).
- Les docstrings explicitent la sémantique de chaque constante.

Compatibilité ascendante : si d'autres modules font ``ParseConstants.DEFAULT_*``,
remplacer l'import par ``from parsing_benevole.settings import constants`` et
accéder via ``constants.DEFAULT_*``, ou adapter les sites d'appel
(recherche/remplacement triviale).
"""

# ---------------------------------------------------------------------------
# Constantes de parcours du fichier
# ---------------------------------------------------------------------------

DEFAULT_MAX_EMPTY_ROWS: int = 5
"""Nombre maximal de lignes vides consécutives tolérées avant d'arrêter le
parcours du fichier."""

DEFAULT_HEADER_ROW: int = 0
"""Index (0-based) de la ligne contenant les en-têtes de colonnes."""

# ---------------------------------------------------------------------------
# Constantes d'extraction des préférences
# ---------------------------------------------------------------------------

DEFAULT_MAX_PREFERENCES: int = 4
"""Nombre maximal de colonnes de préférences à inspecter par bénévole.
Les colonnes sont nommées selon le patron ``preference_pattern`` défini dans
:class:`~parsing_benevole.settings.schema_configuration.SchemaConfiguration`
(ex: ``'(choix 1)'``, ``'(choix 2)'``, …)."""