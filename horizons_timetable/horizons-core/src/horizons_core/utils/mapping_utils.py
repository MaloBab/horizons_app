from typing import Optional
from horizons_core.utils.enums import Pole, PREFERENCES_TO_POSTES
from horizons_core.utils.text_utils import TextUtils

class MappingUtils:
    """Utilitaires pour le mapping des pôles."""

    _POSTE_KEYWORDS_MAP = {
        'pole bar': Pole.BAR,
        'bar': Pole.BAR,
        'pole restauration': Pole.RESTAURATION,
        'restauration': Pole.RESTAURATION,
        'pole catering': Pole.CATERING,
        'catering': Pole.CATERING,
        'pole securite/secours': Pole.SECURITE_SECOURS,
        'securite': Pole.SECURITE_SECOURS,
        'secours': Pole.SECURITE_SECOURS,
        'pole prevention': Pole.PREVENTION,
        'prevention': Pole.PREVENTION,
        'pole ticketterie': Pole.TICKETTERIE,
        'ticketerie': Pole.TICKETTERIE,
        'pole camping': Pole.CAMPING,
        'camping': Pole.CAMPING,
        'pole billetterie': Pole.BILLETTERIE,
        'billetterie': Pole.BILLETTERIE,
        'pole animations': Pole.ANIMATIONS,
        'animations': Pole.ANIMATIONS,
        'pole accueil': Pole.ACCUEIL,
        'accueil': Pole.ACCUEIL,
        'pole acces, parking et riverains': Pole.ACCES_PARKING,
        'acces': Pole.ACCES_PARKING,
        'parking': Pole.ACCES_PARKING,
        'pole environnement': Pole.ENVIRONNEMENT,
        'enviro': Pole.ENVIRONNEMENT,
        'environnement': Pole.ENVIRONNEMENT,
        'accreditations': Pole.ACCREDITATION,
        'accreditation': Pole.ACCREDITATION,
        'pole accreditations': Pole.ACCREDITATION,
        'technique': Pole.TECHNIQUE,
        'pole technique': Pole.TECHNIQUE,
        'technique le dimanche': Pole.TECHNIQUE,
        'technique le vendredi': Pole.TECHNIQUE,
        'technique le samedi': Pole.TECHNIQUE,
        'pole technique le dimanche': Pole.TECHNIQUE,
        'pole technique le vendredi': Pole.TECHNIQUE,
        'pole technique le samedi': Pole.TECHNIQUE,
        'pole production': Pole.ACCUEIL,
        'production': Pole.ACCUEIL,
        'pole autres': Pole.AUTRES,
        'autres': Pole.AUTRES,
    }

    @staticmethod
    def get_pole_id(pole: Optional[str]) -> int:
        """
        Mapping direct (nom exact du pôle).

        Args:
            pole: Le nom du pôle.

        Returns:
            L'ID du pôle ou -1 si non trouvé.
        """
        if pole is None:
            return Pole.AUTRES

        pole_nettoye = TextUtils.nettoyer_texte(pole)
        return MappingUtils._POSTE_KEYWORDS_MAP.get(pole_nettoye, Pole.AUTRES)

    @staticmethod
    def trouver_preference_dans_description(description: Optional[str]) -> Optional[str]:
        """Retourne le premier mot-clé de préférence trouvé dans la description, ou None."""
        if not description:
            return None

        description_propre = TextUtils.nettoyer_texte(description)

        for mot_cle in PREFERENCES_TO_POSTES.keys():
            mot_cle_propre = TextUtils.nettoyer_texte(mot_cle)
            
            if mot_cle_propre in description_propre:
                return mot_cle_propre

        return None