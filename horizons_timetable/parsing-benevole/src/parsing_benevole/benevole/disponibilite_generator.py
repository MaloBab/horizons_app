import logging
from typing import Optional
import re
import math
from horizons_core.dataclass.creneau import Creneau
from horizons_core.exceptions.invalid_timeslot_exception import InvalidTimeslotException
from horizons_core.utils.date_utils import DateUtils
from horizons_core.utils.text_utils import TextUtils

logger = logging.getLogger(__name__)


class DisponibiliteGenerator:
    """Service dédié à la génération des créneaux de disponibilité."""
    
    INDISPOS_VIDES = {
        "ras", "neant", "néant", "aucun", "aucune", "aucun imperatif", "aucun impératif",
        "aucune imperatif", "aucune impératif",
        "pas d'imperatif", "pas d impératif", "pas d imperatif", "pas d'impératif",
        "pas d'imperatifs", "pas d'impératifs", "pas d imperatifs",
        "pas specialement", "pas spécialement",
        "toujours disponible", "n/a", "na",
    }
    

    PATTERN_INDISPO = re.compile(r'(\w+)\s+([0-9]+)h-([0-9]+)h')

    HEURE_MIN_VALIDE = 8
    HEURE_MAX_VALIDE = 30  # 5h du matin jour suivant en notation brute

    def generer(
        self,
        jour_debut: str,
        heure_debut: str,
        jour_fin: str,
        heure_fin: str,
        indispos: Optional[str],
    ) -> tuple[list[Creneau], list[str]]:
        disponibilites: list[Creneau] = []
        warnings: list[str] = []

        try:
            jour_start = DateUtils.convertir_jour_en_int(jour_debut)
            jour_end   = DateUtils.convertir_jour_en_int(jour_fin, jour_precedent=jour_start)

            heure_start_raw = DateUtils.convertir_heure_non_iso(heure_debut)
            # Arrondir à l'heure supérieure si les minutes ne sont pas zéro
            heure_start_raw = self._arrondir_heure_superieure(heure_start_raw, heure_debut)
            
            heure_end_raw   = DateUtils.convertir_heure_non_iso(heure_fin)

            if jour_start > jour_end:
                warnings.append(
                    f"Incohérence de dates : jour de début '{jour_debut}' (jour {jour_start}) "
                    f"est après jour de fin '{jour_fin}' (jour {jour_end}) — "
                    f"aucun créneau généré"
                )
                return [], warnings

            if heure_start_raw < self.HEURE_MIN_VALIDE and heure_start_raw >= 0:
                warnings.append(
                    f"Heure de début '{heure_debut}' ({heure_start_raw}h) hors plage festival "
                    f"({self.HEURE_MIN_VALIDE}h–{self.HEURE_MAX_VALIDE - 24}h) — "
                    f"ajustée au lendemain ({jour_debut} → {heure_start_raw + 24}h brut)"
                )

            heure_start = self._ajuster_heure(heure_start_raw)
            heure_end   = self._ajuster_heure(heure_end_raw)

            if jour_start == jour_end and heure_start >= heure_end:
                warnings.append(
                    f"Heure de début ({heure_debut}) ≥ heure de fin ({heure_fin}) "
                    f"sur le même jour — aucun créneau généré"
                )
                return [], warnings

        except ValueError as e:
            logger.error(f"Erreur conversion dates: {e}")
            raise

        indisponibilites, indispo_warnings = self._parser_indisponibilites(indispos, jour_start)
        warnings.extend(indispo_warnings)

        for jour in range(jour_start, jour_end + 1):
            heure_min = heure_start if jour == jour_start else self.HEURE_MIN_VALIDE
            heure_max = heure_end   if jour == jour_end   else self.HEURE_MAX_VALIDE

            for heure in range(heure_min, heure_max):
                try:
                    creneau = Creneau(heure, heure + 1, jour)
                    if not self._est_indisponible(creneau, indisponibilites):
                        disponibilites.append(creneau)
                except InvalidTimeslotException as e:
                    msg = (
                        f"Créneau ignoré — {jour_debut} {heure % 24}h–{(heure + 1) % 24}h "
                        f"(heure brute {heure}) : {e}"
                    )
                    logger.warning(msg)
                    warnings.append(msg)

        return disponibilites, warnings

    def _ajuster_heure(self, heure: int) -> int:
        return heure + 24 if heure < self.HEURE_MIN_VALIDE else heure

    def _extraire_minutes(self, heure_str: str) -> int:
        """Extrait les minutes d'une chaîne d'heure (ex: '18:20' → 20)."""
        try:
            heure_nettoye = TextUtils.nettoyer_texte(heure_str)
            heure_nettoye = re.sub(r'\s*[ap]m\s*', '', heure_nettoye, flags=re.IGNORECASE).strip()
            heure_nettoye = heure_nettoye.replace('h', ':')
            parts = heure_nettoye.split(':')
            if len(parts) >= 2:
                return int(parts[1].strip())
        except (ValueError, IndexError):
            pass
        return 0

    def _arrondir_heure_superieure(self, heure_brute: int, heure_str: str) -> int:
        """Arrondit à l'heure supérieure si les minutes ne sont pas zéro."""
        minutes = self._extraire_minutes(heure_str)
        if minutes > 0:
            return heure_brute + 1
        return heure_brute

    def _parser_indisponibilites(
        self, indispos: Optional[str], jour_debut: int
    ) -> tuple[set[Creneau], list[str]]:
        warnings: list[str] = []

        if not indispos or not indispos.strip() or indispos.startswith("//"):
            return set(), warnings

        indispos_nettoye = TextUtils.nettoyer_texte(indispos)

        if (
            not indispos_nettoye
            or indispos_nettoye in self.INDISPOS_VIDES
            or indispos_nettoye.startswith("non")
            or indispos_nettoye.startswith("pas ")
        ):
            return set(), warnings

        indisponibilites: set[Creneau] = set()

        for part in indispos_nettoye.split(','):
            part = part.strip()
            if not part:
                continue
            match = self.PATTERN_INDISPO.match(part)
            if match:
                try:
                    jour       = DateUtils.convertir_jour_en_int(
                                    match.group(1), jour_precedent=jour_debut)
                    heure_deb  = self._ajuster_heure(int(match.group(2)))
                    heure_fin_ = self._ajuster_heure(int(match.group(3)))
                    indisponibilites.add(Creneau(heure_deb, heure_fin_, jour))
                except (ValueError, InvalidTimeslotException) as e:
                    msg = f"Indisponibilité invalide '{part}': {e}"
                    logger.warning(msg)
                    warnings.append(msg)
            else:
                msg = f"Format d'indisponibilité non reconnu : '{part}'"
                logger.warning(msg)
                warnings.append(msg)

        return indisponibilites, warnings

    def _est_indisponible(self, creneau: Creneau, indisponibilites: set[Creneau]) -> bool:
        return any(creneau.is_inclued_in(indispo) for indispo in indisponibilites)