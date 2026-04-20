"""
Modules utilitaires pour la gestion des dates, du mapping et du texte.
"""

from enum import Enum, IntEnum

class RecruitmentType(Enum):
    NORMAL     = 'Normal'
    SPECIALISE = 'Specialise'

class JourSemaine(IntEnum):
    """Énumération des jours de la semaine."""
    LUNDI = 0
    MARDI = 1
    MERCREDI = 2
    JEUDI = 3
    VENDREDI = 4
    SAMEDI = 5
    DIMANCHE = 6


class Pole(IntEnum):
    """Énumération des pôles."""
    BAR = 1
    RESTAURATION = 2
    CATERING = 3
    SECURITE_SECOURS = 4
    PREVENTION = 5
    TICKETTERIE = 6
    CAMPING = 7
    BILLETTERIE = 8
    ANIMATIONS = 9
    ACCUEIL = 10
    ACCES_PARKING = 11
    ENVIRONNEMENT = 12
    ACCREDITATION = 13
    TECHNIQUE = 14
    AUTRES = 15
    

PREFERENCES_TO_POSTES : dict[str, list] = {
"accueil du public" : [Pole.BILLETTERIE, Pole.CAMPING, Pole.ACCES_PARKING, Pole.SECURITE_SECOURS, Pole.AUTRES],
"ravitaillement" : [Pole.BAR, Pole.RESTAURATION, Pole.CATERING],
"vie sur site" : [Pole.ACCUEIL, Pole.TICKETTERIE, Pole.ANIMATIONS, Pole.ENVIRONNEMENT, Pole.PREVENTION],
"logistique" : [Pole.ACCREDITATION, Pole.TECHNIQUE],
}
