import re
from typing import Optional
from horizons_core.utils.enums import JourSemaine
from horizons_core.utils.text_utils import TextUtils

class DateUtils:
    """Utilitaires pour la gestion des dates et heures."""

    _JOURS_MAPPING = {
        'lundi': JourSemaine.LUNDI,
        'mardi': JourSemaine.MARDI,
        'mercredi': JourSemaine.MERCREDI,
        'jeudi': JourSemaine.JEUDI,
        'vendredi': JourSemaine.VENDREDI,
        'samedi': JourSemaine.SAMEDI,
        'dimanche': JourSemaine.DIMANCHE,
    }

    @staticmethod
    def convertir_jour_en_int(jour: Optional[str], jour_precedent: Optional[int] = None) -> int:
        """
        Convertit un jour en entier (0-6 normaux, 7 = lundi suivant).
        
        LOGIQUE SPÉCIALE :
        - Si jour_precedent existe ET jour actuel < jour_precedent → on boucle sur la semaine
        - Donc Lundi après n'importe quel jour >= Mardi → jour 7
        
        Example:
            >>> DateUtils.convertir_jour_en_int("jeudi")
            3
            >>> DateUtils.convertir_jour_en_int("lundi", jour_precedent=3)
            7  Lundi APRÈS Jeudi = semaine suivante
        """
        if jour is None:
            raise ValueError("Le jour ne peut pas être None")

        jour_nettoye = TextUtils.nettoyer_texte(jour)
        premier_mot = jour_nettoye.split()[0] if jour_nettoye else ""

        if premier_mot not in DateUtils._JOURS_MAPPING:
            raise ValueError(f"Jour invalide : {jour}")

        jour_value = DateUtils._JOURS_MAPPING[premier_mot]
        
        if jour_precedent is not None and jour_value < jour_precedent:
            if jour_value == JourSemaine.LUNDI:
                return 7
        return jour_value

    @staticmethod
    def convertir_heure_non_iso(heure: Optional[str]) -> int:
        """
        Convertit une heure non ISO (ex: "8h", "08:00", "6:30 pm", "5:00:00 PM") 
        en entier (nombre d'heures).

        Args:
            heure: L'heure à convertir.

        Returns:
            L'heure en format 24h.

        Raises:
            ValueError: Si le format d'heure est invalide ou None.
        """
        if heure is None:
            raise ValueError("L'heure ne peut pas être None")

        h = TextUtils.nettoyer_texte(heure)
        
        if not h:
            raise ValueError(f"L'heure est vide après nettoyage : '{heure}'")

        is_pm = 'pm' in h
        is_am = 'am' in h

        h = re.sub(r'\s*[ap]m\s*', '', h, flags=re.IGNORECASE)
        h = h.strip()
        h = h.replace('h', ':')
        parts = h.split(':')
        
        try:
            hour = int(parts[0].strip())
            if is_pm and hour < 12:
                hour += 12
            elif is_am and hour == 12:
                hour = 0

            if hour < 0 or hour > 30: 
                raise ValueError(f"Heure hors limites : {hour}")

            return hour

        except (ValueError, IndexError) as e:
            raise ValueError(f"Format d'heure invalide : '{heure}' (nettoyé: '{h}')") from e
        