from horizons_core.ods.column_indexer import ColumnIndexer
from parsing_benevole.settings.schema_configuration import SchemaConfiguration


class ColumnHelper:
    """Helper pour accéder aux colonnes via le schéma.

    Fait le pont entre les clés sémantiques du schéma (ex: ``'nom'``,
    ``'email'``) et les indices de colonnes physiques du fichier ODS.

    """

    def __init__(self, schema: SchemaConfiguration, indexer: ColumnIndexer) -> None:
        """Initialise le helper.

        Args:
            schema:  Configuration du schéma de colonnes.  Son dictionnaire
                     est construit **ici une seule fois** et réutilisé pour
                     tous les appels suivants à :meth:`get_column_index`.
            indexer: Indexeur de colonnes déjà initialisé sur la feuille ODS.
        """
        # On matérialise le dictionnaire schéma une bonne fois pour toutes.
        # SchemaConfiguration est immuable après construction (dataclass sans
        # setters publics), donc cette capture est sûre pour toute la durée
        # de vie de l'objet.
        self._schema_dict: dict[str, str] = schema.to_dict()
        self._indexer = indexer
        # Cache clé-sémantique → index physique, rempli à la demande.
        self._cache: dict[str, int] = {}

    def get_column_index(self, cle_colonne: str) -> int:
        """Retourne l'index physique de la colonne identifiée par cle_colonne.

        Args:
            cle_colonne: Clé sémantique définie dans :class:`SchemaConfiguration`
                         (ex: ``'nom'``, ``'email'``, ``'jour_debut'``) **ou**
                         libellé brut si la clé n'est pas dans le schéma.

        Returns:
            Index (0-based) de la colonne dans la feuille ODS.

        Raises:
            KeyError: Si aucune colonne ne correspond, avec un message indiquant
                      à la fois la clé sémantique et le libellé recherché.
        """
        if cle_colonne in self._cache:
            return self._cache[cle_colonne]

        keyword = self._schema_dict.get(cle_colonne, cle_colonne)

        try:
            col_index = self._indexer.get_column_index(keyword)
        except KeyError as exc:
            raise KeyError(
                f"Colonne '{keyword}' (clé: '{cle_colonne}') introuvable dans la feuille ODS"
            ) from exc

        self._cache[cle_colonne] = col_index
        return col_index