from dataclasses import dataclass

@dataclass(frozen=True)
class PosteConfig:
    """Configuration du parsing de postes (extensible sans modifier le code)."""
    
    col_nom_responsible: int = 1
    col_nom_poste: int = 2  
    col_type_poste: int = 4  
    
    row_debut_postes: int = 5 
    row_max: int = 150 
    row_jours: int = 0 
    row_heures: int = 4 
    
    col_offset_debut_creneaux: int = 4
    creneaux_par_jour: int = 23   
    
    type_poste_normal: str = "normal"