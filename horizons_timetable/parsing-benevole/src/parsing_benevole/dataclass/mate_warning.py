"""Value objects liés au matching de compagnons.

Ce module est volontairement isolé pour éviter les imports circulaires :
``compagnon_matcher`` et ``interfaces`` en ont tous les deux besoin, et ne
peuvent pas s'importer mutuellement.
"""

from dataclasses import dataclass


@dataclass
class MateWarning:
    """Warning de non-matching rattaché à un bénévole précis.

    Attributes:
        benevole_name: Nom complet du bénévole déclarant le compagnon.
        comp_name:     Nom du compagnon tel que saisi (nom original).
        message:       Message lisible décrivant la raison du non-matching.
    """

    benevole_name: str
    comp_name: str
    message: str