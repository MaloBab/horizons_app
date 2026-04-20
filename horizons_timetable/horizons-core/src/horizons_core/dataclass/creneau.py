from horizons_core.exceptions.invalid_timeslot_exception import InvalidTimeslotException


class Creneau():
    """
    Créneau horaire pour le festival.
    
    MODIFICATION : Gestion du Lundi post-festival (jour 7)
     
    Attributes:
        borne_inf : heure de début (entre 8h et 29h)
        borne_sup : heure de fin (entre 9h et 30h)
        jour : entier entre 0 et 7
            - 0 = Lundi (avant le festival, non utilisé)
            - 1 = Mardi
            - 2 = Mercredi
            - 3 = Jeudi
            - 4 = Vendredi
            - 5 = Samedi
            - 6 = Dimanche
            - 7 = Lundi (après le festival) ✨ NOUVEAU
    """

    def __init__(self, borne_inf: int, borne_sup: int, jour: int):
        if borne_inf in (6, 7) or borne_sup in (6, 7) or borne_inf > 29 or borne_sup > 30:
            raise InvalidTimeslotException(
                f"Saisie erronée : Heures invalides. "
                f"Les heures doivent être comprises entre 8h et 6h (le lendemain) : "
                f"{borne_inf}h - {borne_sup}h - jour {jour}"
            )

        if borne_inf >= borne_sup and borne_sup != 8:
            raise InvalidTimeslotException(
                "Saisie erronée : Heure de début supérieure ou égale à l'heure de fin."
            )

        if jour < 0 or jour > 7:
            raise InvalidTimeslotException(
                f"Saisie erronée : Jour invalide ({jour}). Doit être entre 0 et 7."
            )

        self._borne_inf = borne_inf
        self._borne_sup = borne_sup
        self._jour = jour

    def get_jour(self) -> int:
        return self._jour

    def get_borne_inf(self) -> int:
        return self._borne_inf

    def get_borne_sup(self) -> int:
        return self._borne_sup

    def is_inclued_in(self, c: "Creneau") -> bool:
        """
        Retourne True si ce créneau est inclus dans le créneau donné.
        """
        return (
            c.get_borne_inf() <= self._borne_inf
            and c.get_borne_sup() >= self._borne_sup
            and self._jour == c.get_jour()
        )

    def is_incompatible(self, c: "Creneau") -> bool:
        """
        Retourne True si les créneaux se chevauchent le même jour.
        """
        if self._jour != c.get_jour():
            return False
        return not (self._borne_sup <= c.get_borne_inf() or c.get_borne_sup() <= self._borne_inf)

    def __eq__(self, other):
        if not isinstance(other, Creneau):
            return False
        return (
            self._jour == other._jour
            and self._borne_inf == other._borne_inf
            and self._borne_sup == other._borne_sup
        )

    def __hash__(self):
        return hash((self._jour, self._borne_inf, self._borne_sup))

    def __str__(self):
        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche", "Lundi (suivant)"]

        inf = self._borne_inf - 24 if self._borne_inf > 23 else self._borne_inf
        sup = self._borne_sup - 24 if self._borne_sup > 23 else self._borne_sup

        jour_debut_idx = self._jour if self._jour <= 6 else 7
        jour_fin_idx = self._jour if self._jour <= 6 else 7
        
        if self._borne_inf > 23:
            jour_debut_idx = (self._jour + 1) % 8 if self._jour < 7 else 7
        if self._borne_sup > 23:
            jour_fin_idx = (self._jour + 1) % 8 if self._jour < 7 else 7

        jour_debut = jours[jour_debut_idx]
        jour_fin = jours[jour_fin_idx]

        return f"{jour_debut} : {inf}h - {jour_fin} {sup}h"