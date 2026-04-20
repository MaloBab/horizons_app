from dataclasses import dataclass

@dataclass(frozen=True)
class Categorie:
    """Représente un pôle/catégorie.
    
    Le responsable est désormais porté par chaque Poste individuellement.
    """
    nom:     str
    pole_id: int

    def __str__(self) -> str:
        return f"[{self.pole_id}] {self.nom}" 