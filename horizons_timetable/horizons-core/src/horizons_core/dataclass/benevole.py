
from copy import deepcopy
from horizons_core.dataclass.creneau import Creneau
from horizons_core.utils.enums import RecruitmentType

class Benevole():
    def __init__(
        self,
        nom: str,
        prenom: str,
        mail: str,
        adresse: str,
        numero_tel: str,
        disponibilites: list[Creneau],
        preferences: list[str],
        type_benevole: RecruitmentType
    ):
        self._id : str
        self._nom = nom
        self._prenom = prenom
        self._mail = mail
        self._adresse = adresse
        self._type_benevole = type_benevole
        self._numero_tel = numero_tel
        self._disponibilites = list(disponibilites)
        self._preferences = list(preferences)
        self._compagnons: set[Benevole] = set()

    def get_id(self) -> str:
        return self._id
    
    def get_name(self) -> str:
        return f"{self._nom} {self._prenom}"
    
    def get_nom(self) -> str:
        return self._nom

    def get_prenom(self) -> str:
        return self._prenom

    def get_mail(self) -> str:
        return self._mail

    def get_adresse(self) -> str:
        return self._adresse

    def get_numero_tel(self) -> str:
        return self._numero_tel

    def get_type_benevole(self) -> RecruitmentType:
        return self._type_benevole

    def get_preferences(self) -> list[str]:
        return self._preferences.copy()

    def get_disponibilites(self) -> list[Creneau]:
        return list(self._disponibilites)

    def get_compagnons(self) -> frozenset['Benevole']:
        return frozenset(self._compagnons)
    
    def get_compagnons_emails(self) -> list[str]:
        return [c.get_mail() for c in self._compagnons]
    
    def set_id(self, id: str) -> None:
        self._id = id
    
    def add_compagnon(self, benevole: "Benevole") -> None:
        """Ajoute un compagnon."""
        self._compagnons.add(benevole)

    def is_disponible(self, c: Creneau) -> bool:
        """Vérifie si le bénévole couvre entièrement le créneau donné."""
        jour = c.get_jour()
        heures_couvertes: set[int] = {
            heure
            for dispo in self._disponibilites
            if dispo.get_jour() == jour
            for heure in range(dispo.get_borne_inf(), dispo.get_borne_sup())
        }
        return all(heure in heures_couvertes for heure in range(c.get_borne_inf(), c.get_borne_sup()))
 

    def clone(self) -> "Benevole":
        disponibilite_copy = [deepcopy(c) for c in self._disponibilites]
        copie = Benevole(
            self._nom,
            self._prenom,
            self._mail,
            self._adresse,
            self._numero_tel,
            disponibilite_copy,
            deepcopy(self._preferences),
            self._type_benevole
        )
        copie._compagnons.update(self._compagnons)
        return copie

    def __eq__(self, other):
        return (
            isinstance(other, Benevole)
            and self._nom == other._nom
            and self._prenom == other._prenom
            and self._mail == other._mail
            and self._adresse == other._adresse
        )

    def __hash__(self):
        return hash((self._nom, self._prenom, self._mail, self._adresse))

    def __str__(self):
        result = []
        result.append("---------------")
        result.append(f"Nom: {self._nom}")
        result.append(f"Prénom: {self._prenom}")
        result.append(f"Mail: {self._mail}")
        result.append(f"Type de bénévole: {self._type_benevole.value}")
        result.append(f"Adresse: {self._adresse}")
        result.append(f"Téléphone: {self._numero_tel}")
        prefs = ", ".join(str(p) for p in self._preferences)
        result.append(f"Préférences: [{prefs}]")
        result.append("Disponibilités:")
        for c in self._disponibilites:
            result.append(f"  {c}")
        result.append("Affinités:")
        for b in self._compagnons:
            result.append(f"  {b.get_name()}")
        result.append("---------------\n")
        return "\n".join(result)