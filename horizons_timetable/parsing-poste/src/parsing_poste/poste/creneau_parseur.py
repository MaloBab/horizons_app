import logging
from parsing_poste.settings.poste_config import PosteConfig
from parsing_poste.interfaces.interfaces import IJourDetector, ICreneauParser

from horizons_core.ods.sheet_reader import SheetReader
from horizons_core.ods.cell_span_detector import CellSpanDetector

from horizons_core.dataclass.creneau import Creneau
from horizons_core.exceptions.invalid_timeslot_exception import InvalidTimeslotException


logger = logging.getLogger(__name__)

class CreneauParser(ICreneauParser):
    """Parse les créneaux horaires d'une ligne de poste.
    
    RESPONSABILITÉ : Extraction des créneaux depuis les cellules fusionnées
    RÉUTILISE : 
    - CellSpanDetector pour détecter les fusions
    - Creneau pour créer les objets
    - DateUtils pour conversion des heures
    """
    
    def __init__(
        self,
        sheet: SheetReader,
        config: PosteConfig,
        span_detector: CellSpanDetector,
        jour_detector: IJourDetector
    ):
        """Initialise le parser de créneaux."""
        self._sheet = sheet
        self._config = config
        self._span_detector = span_detector
        self._jour_detector = jour_detector
    
    def parse_creneaux_ligne(self, row: int) -> list[Creneau]:
        """Parse tous les créneaux d'une ligne.
        
        1. Scanner les colonnes de créneaux (col >= col_offset_debut_creneaux)
        2. Pour chaque cellule non vide :
           - Récupérer l'heure de début (depuis ligne row_heures)
           - Détecter le jour (via jour_detector)
           - Calculer heure de fin (heure_debut + colspan)
           - Créer le Creneau
        3. Sauter les colonnes fusionnées (col += colspan)
        """
        creneaux = []
        col = self._config.col_offset_debut_creneaux + 1  # Colonne F (index 5)
        
        while col < self._sheet.get_column_count():
            try:
                # 1. Récupérer l'heure de début depuis la ligne des heures
                heure_str = self._sheet.get_value(self._config.row_heures, col)
                
                if not heure_str or not heure_str.strip():
                    break  # Fin des créneaux
                
                heure_debut = int(heure_str.strip())
                
                # 2. Récupérer le jour de la colonne
                jour = self._jour_detector.get_jour_from_column(col)
                if jour == -1:
                    logger.warning(f"Jour invalide pour colonne {col}, ligne {row}")
                    col += 1
                    continue
                
                # 3. Vérifier si la cellule du poste est non vide
                cell_value = self._sheet.get_value(row, col)
                
                if cell_value and cell_value.strip():
                    # 4. Détecter le colspan pour calculer la durée
                    colspan = self._span_detector.get_colspan(row, col)
                    
                    # 5. Calculer les bornes horaires
                    borne_inf = heure_debut if heure_debut >= 8 else heure_debut + 24
                    borne_sup = borne_inf + colspan
                    
                    # 6. Créer le créneau
                    creneau = Creneau(borne_inf, borne_sup, jour)
                    creneaux.append(creneau)
                    
                    # 7. Sauter les colonnes fusionnées
                    col += colspan
                else:
                    col += 1
                    
            except (ValueError, InvalidTimeslotException) as e:
                logger.warning(f"Erreur parsing créneau ligne {row}, col {col}: {e}")
                col += 1
            except IndexError:
                break
        
        return creneaux