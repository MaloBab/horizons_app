# 🧬 Algorithme Génétique - Affectation Bénévoles

## 📋 Architecture

```
genetic/
├── core/
│   ├── chromosome.py           # Représentation d'une solution
│   └── population.py            # Gestion de population
├── fitness/
│   └── fitness_calculator.py   # Calcul du fitness modulaire
├── operators/
│   ├── initializer.py          # Initialisation de population
│   ├── crossover.py            # Opérateur de croisement
│   └── mutation.py             # Opérateur de mutation
├── repair/
│   ├── constraint_validator.py # Validation des contraintes
│   └── solution_repairer.py    # Réparation de solutions
├── export/
│   └── ods_exporter.py         # Export ODS/Excel
├── config.py                   # Configuration centralisée
└── engine.py                   # Moteur principal
```

## 🚀 Utilisation

### Installation

```bash
pip install -r requirements.
```

### Execution
```bash 
python -m PYTHON.main.py "C:/Users/Malo Babinot/Desktop/Programmation/Horizons/documents/fichiers de tests/Besoins bénévoles 2025.2.ods" "C:/Users/Malo Babinot/Desktop/Programmation/Horizons/documents/fichiers de tests/Inscriptions Bénévoles Horizons 2025 (réponses).ods" 
```

### Configuration

Modifier les paramètres dans `main.py` :

```python
config = GeneticConfig(
    population_size=1000,      # Taille de population
    generations=500,           # Nombre de générations
    mutation_rate=0.06,        # Taux de mutation
    elite_count=5,            # Élitisme
    tournament_size=10        # Taille du tournoi
)
```

### Poids du fitness

Personnaliser les poids dans `FitnessWeights` :

```python
weights = FitnessWeights(
    benevole_affecte=1000.0,
    preference_match=10.0,
    compagnon_travaille_ensemble=80.0,
    surcharge_journaliere=-20000.0
)
```

## 🎯 Fonctionnalités

### ✅ Implémenté

- ✅ Algorithme génétique standard (sélection, crossover, mutation)
- ✅ Fitness multi-critères configurable
- ✅ Élitisme
- ✅ Validation des contraintes
- ✅ Réparation automatique des solutions
- ✅ Export ODS/Excel
- ✅ Logging détaillé
- ✅ Réutilisation maximale du code existant (parseurs)

### 📊 Critères du Fitness

**Critères positifs:**

- Bénévoles affectés
- Postes remplis
- Préférences respectées
- Compagnons travaillant ensemble

**Pénalités:**

- Bénévoles non affectés
- Postes non remplis
- Créneaux consécutifs
- Surcharge de travail (>6h/jour)

## 🔧 Améliorations vs Code Java

1. **Architecture modulaire** (SOLID)
2. **Fitness configurable** (poids externalisés)
3. **Validation séparée** (contraintes dures/souples)
4. **Réparation post-génétique** (amélioration locale)
5. **Export professionnel** (ODS/Excel)
6. **Logging structuré**
7. **Réutilisation maximale** (parseurs existants)

## 📈 Performance

- **Population:** 1000 individus
- **Générations:** 500
- **Temps estimé:** 10-30 minutes (dépend du nombre de postes/bénévoles)

## 🐛 Debug

Activer le mode debug dans `main.py` :

```python
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Licence

MIT
