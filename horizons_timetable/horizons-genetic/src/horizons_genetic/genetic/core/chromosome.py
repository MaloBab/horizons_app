from dataclasses import dataclass, field
from typing import  Optional
from horizons_core.dataclass.poste import Poste
from horizons_core.dataclass.benevole import Benevole


@dataclass
class Chromosome:
    """
    Représente une solution complète (affectation bénévoles -> postes).
    
    IMMUTABILITÉ : Les affectations sont copiées pour éviter les effets de bord
    RESPONSABILITÉ : Container de données + opérations de base
    """
    
    affectations: dict[Poste, list[Benevole]] = field(default_factory=dict)
    _fitness: Optional[float] = field(default=None, init=False, repr=False)
    _raw_scores: Optional[dict[str, float]] = field(default=None, init=False, repr=False)
    
    def get_fitness(self) -> Optional[float]:
        """Retourne le fitness (None si pas encore évalué)."""
        return self._fitness
    
    def set_fitness(self, fitness: float, raw_scores: Optional[dict[str, float]] = None) -> None:
        """Définit le fitness et optionnellement les scores détaillés."""
        self._fitness = fitness
        self._raw_scores = raw_scores
    
    def get_raw_scores(self) -> Optional[dict[str, float]]:
        """Retourne les scores détaillés si disponibles."""
        return self._raw_scores
    
    def clone(self) -> 'Chromosome':
        """Crée une copie profonde du chromosome."""
        return Chromosome(
            affectations={
                poste: benevoles.copy()
                for poste, benevoles in self.affectations.items()
            }
        )
    
    def get_benevole_assignments(self) -> dict[Benevole, list[Poste]]:
        """Retourne l'inverse : bénévole -> liste de postes."""
        benevole_to_postes: dict[Benevole, list[Poste]] = {}
        for poste, benevoles in self.affectations.items():
            for benevole in benevoles:
                if benevole is not None:
                    benevole_to_postes.setdefault(benevole, []).append(poste)
        return benevole_to_postes
    
    def count_filled_positions(self) -> int:
        """Compte le nombre de positions remplies."""
        return sum(
            1 for benevoles in self.affectations.values()
            for b in benevoles if b is not None
        )
    
    def count_total_positions(self) -> int:
        """Compte le nombre total de positions."""
        return sum(len(benevoles) for benevoles in self.affectations.values())
    
    def get_assigned_benevoles(self) -> set:
        """Retourne l'ensemble des bénévoles affectés."""
        assigned = set()
        for benevoles in self.affectations.values():
            assigned.update(b for b in benevoles if b is not None)
        return assigned
    
    def __eq__(self, other):
        return isinstance(other, Chromosome) and self.affectations == other.affectations
    
    def __hash__(self):
        return hash(frozenset(self.affectations.keys()))
    

@dataclass
class LightweightChromosome:
    """
    Représentation optimisée d'une solution (indices uniquement).
    
    OPTIMISATIONS:
    - Stockage par indices (int8/int16) au lieu d'objets Python
    - Clone ultra-rapide (copie d'arrays NumPy)
    - Cache du fitness et des scores détaillés
    - Méthodes de conversion lazy (objets créés à la demande)
    
    Structure:
        poste_to_benevoles: dict[int, list[int]]
            clé: ID du poste
            valeur: liste des IDs de bénévoles (-1 = position vide)

    CORRECTION BUG HASH :
        Le hash prenait uniquement les clés (poste IDs), identiques pour tous
        les chromosomes → collisions garanties dans les sets/dicts.
        Il prend maintenant le contenu complet (clés + valeurs).
    """
    
    poste_to_benevoles: dict[int, list[int]] = field(default_factory=dict)
    _fitness: Optional[float] = field(default=None, init=False, repr=False)
    _raw_scores: Optional[dict[str, float]] = field(default=None, init=False, repr=False)
    _hash_cache: Optional[int] = field(default=None, init=False, repr=False)
    
    _poste_index: Optional[dict] = field(default=None, init=False, repr=False)
    _benevole_index: Optional[dict] = field(default=None, init=False, repr=False)
    
    def get_fitness(self) -> Optional[float]:
        if self._fitness is None:
            return None
        return self._fitness
    
    def set_fitness(self, fitness: float, raw_scores: Optional[dict[str, float]] = None):
        self._fitness = fitness
        self._raw_scores = raw_scores
        self._hash_cache = None  
    
    def get_raw_scores(self) -> Optional[dict[str, float]]:
        return self._raw_scores
    
    def clone(self) -> 'LightweightChromosome':
        """Clone ultra-rapide (copie de dictionnaire d'entiers)."""
        cloned = LightweightChromosome(
            poste_to_benevoles={
                poste_id: benevoles.copy() 
                for poste_id, benevoles in self.poste_to_benevoles.items()
            }
        )
        cloned._poste_index = self._poste_index
        cloned._benevole_index = self._benevole_index
        return cloned
    
    def get_benevole_assignments(self) -> dict[int, list[int]]:
        """Retourne l'inverse: benevole_id -> [poste_ids]."""
        benevole_to_postes: dict[int, list[int]] = {}
        
        for poste_id, benevoles in self.poste_to_benevoles.items():
            for benevole_id in benevoles:
                if benevole_id >= 0:
                    benevole_to_postes.setdefault(benevole_id, []).append(poste_id)
        
        return benevole_to_postes
    
    def count_filled_positions(self) -> int:
        """Compte les positions remplies."""
        return sum(
            1 for benevoles in self.poste_to_benevoles.values()
            for b_id in benevoles if b_id >= 0
        )
    
    def count_total_positions(self) -> int:
        """Compte le nombre total de positions."""
        return sum(len(benevoles) for benevoles in self.poste_to_benevoles.values())
    
    def get_assigned_benevoles(self) -> set[int]:
        """Retourne l'ensemble des IDs de bénévoles affectés."""
        assigned = set()
        for benevoles in self.poste_to_benevoles.values():
            assigned.update(b_id for b_id in benevoles if b_id >= 0)
        return assigned
    
    def __eq__(self, other):
        if not isinstance(other, LightweightChromosome):
            return False
        return self.poste_to_benevoles == other.poste_to_benevoles
    
    def __hash__(self):
        """
        FIX : hash basé sur le contenu complet (clés + valeurs).
        L'ancienne implémentation n'utilisait que les clés (poste IDs),
        identiques pour tous les chromosomes → tous avaient le même hash.
        """
        if self._hash_cache is None:
            self._hash_cache = hash(
                frozenset(
                    (k, tuple(v))
                    for k, v in self.poste_to_benevoles.items()
                )
            )
        return self._hash_cache