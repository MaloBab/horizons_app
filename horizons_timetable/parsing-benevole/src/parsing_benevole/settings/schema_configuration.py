from dataclasses import dataclass, asdict
import json

@dataclass
class SchemaConfiguration:
    """Configuration externalisable du schéma de colonnes.
    
    Permet de supporter différents formats de fichiers sans modifier le code.
    
    Example:
        >>> config = SchemaConfiguration.from_json("schema.json")
        >>> config = SchemaConfiguration(nom="Nom complet", email="Courriel")
    """
    nom: str = 'nom'
    prenom: str = 'prenom'
    email: str = 'e-mail'
    telephone: str = 'numero de telephone'
    adresse: str = 'adresse postale'
    jour_debut: str = 'arriver sur le site'
    heure_debut: str = 'a quelle heure ?'
    jour_fin: str = 'partir du site'
    heure_fin: str = 'a quelle heure ? 2'
    indispos: str = 'imperatif'
    compagnons: str = 'ami·e·s, famille'
    intervalle: str = 'benevole avant/apres le festival ou pendant le festival'
    autres_missions: str = 'autres missions pendant le festival'
    preference_pattern: str = '(choix {index})'
    type_benevole: str = 'poste de benevole specialise'
    
    @classmethod
    def from_json(cls, filepath: str) -> 'SchemaConfiguration':
        """Charge la configuration depuis un fichier JSON."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)
    
    def to_dict(self) -> dict[str, str]:
        """Convertit en dictionnaire."""
        return asdict(self)
    
    def get_preference_column(self, index: int) -> str:
        """Retourne le nom de colonne pour une préférence donnée."""
        return self.preference_pattern.format(index=index)