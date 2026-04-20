"""Service de matching des compagnons avec fuzzy matching avancé."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Optional

from horizons_core.dataclass.benevole import Benevole
from horizons_core.utils.text_utils import TextUtils
from parsing_benevole.dataclass.compagnon_data import CompagnonData
from parsing_benevole.dataclass.mate_warning import MateWarning 

logger = logging.getLogger(__name__)


@dataclass
class MatchCandidate:
    """Candidat intermédiaire produit par les stratégies de matching."""

    benevole: Benevole
    score: float
    method: str


class CompagnonMatcher:
    """Service de matching des compagnons avec fuzzy matching avancé.

    Stratégies de matching tentées dans l'ordre :

    1. **Exact** — correspondance directe après normalisation agressive.
    2. **Token** — intersection de tokens (mots) entre le nom recherché et
       les noms indexés ; score = Jaccard sur les tokens.
    3. **Levenshtein** — distance d'édition sur les noms complets normalisés,
       avec seuil adaptatif selon la longueur du nom.

    Le meilleur candidat au-dessus de ``min_confidence`` est retenu.
    """

    def __init__(
        self,
        levenshtein_threshold_short: int = 2,
        levenshtein_threshold_long: int = 3,
        min_confidence: float = 0.6,
    ) -> None:
        self._levenshtein_threshold_short = levenshtein_threshold_short
        self._levenshtein_threshold_long = levenshtein_threshold_long
        self._min_confidence = min_confidence

        # Clé : nom normalisé → bénévole (lookup O(1))
        self._benevole_index: dict[str, Benevole] = {}
        # Clé : token → ensemble des bénévoles qui le contiennent
        self._token_index: dict[str, set[Benevole]] = {}
        # Clé : prénom normalisé → liste de bénévoles (non utilisé en matching
        # direct mais utile pour des extensions futures)
        self._prenom_index: dict[str, list[Benevole]] = {}

    # =========================================================================
    # Interface publique (ICompagnonMatcher)
    # =========================================================================

    def construire_index(self, benevoles: list[Benevole]) -> None:
        """Construit (ou reconstruit) l'index de recherche rapide.

        Args:
            benevoles: Liste complète des bénévoles à indexer.
        """
        self._benevole_index.clear()
        self._token_index.clear()
        self._prenom_index.clear()

        for benevole in benevoles:
            name_normalized = self._normalize_aggressive(benevole.get_name())
            self._benevole_index[name_normalized] = benevole

            tokens = name_normalized.split()
            for token in tokens:
                if len(token) >= 2:
                    self._token_index.setdefault(token, set()).add(benevole)

            if tokens:
                prenom = tokens[-1]
                self._prenom_index.setdefault(prenom, []).append(benevole)

        logger.info(
            "Index construit : %d bénévoles, %d tokens uniques",
            len(self._benevole_index),
            len(self._token_index),
        )

    def associer_compagnons(
        self,
        benevoles: list[Benevole],
        compagnons_data: list[CompagnonData],
    ) -> list[MateWarning]:
        """Associe les compagnons avec fuzzy matching avancé.

        Le matching tente toutes les variantes de ``compagnons_names``.
        Les warnings n'utilisent que ``original_names`` — un warning par nom
        original non trouvé, sans doublon dû aux variantes inversées.

        Args:
            benevoles:       Liste complète des bénévoles (pour construire
                             l'index si ce n'est pas déjà fait).
            compagnons_data: Données de compagnonnage extraites du fichier.

        Returns:
            Liste de :class:`~parsing_benevole.mate_warning.MateWarning`
            rattachés au bénévole déclarant.
        """
        if not self._benevole_index:
            self.construire_index(benevoles)

        total_associations = 0
        total_tentatives = 0
        warnings: list[MateWarning] = []

        for data in compagnons_data:
            benevole_name_normalized = self._normalize_aggressive(data.benevole_name)
            benevole = self._benevole_index.get(benevole_name_normalized)

            if not benevole:
                logger.warning("Bénévole source introuvable : %s", data.benevole_name)
                warnings.append(MateWarning(
                    benevole_name=data.benevole_name,
                    comp_name=data.benevole_name,
                    message=f"Bénévole source introuvable dans l'index : '{data.benevole_name}'",
                ))
                continue

            # Phase 1 — matching sur toutes les variantes (originaux + inversés)
            matched_keys: set[str] = set()

            for comp_name in data.compagnons_names:
                total_tentatives += 1
                comp_normalized = self._normalize_aggressive(comp_name)
                # Clé de déduplication insensible à l'ordre des tokens
                dedup_key = " ".join(sorted(comp_normalized.split()))
                compagnon = self._find_best_match(comp_normalized)

                if compagnon:
                    benevole.add_compagnon(compagnon)
                    total_associations += 1
                    matched_keys.add(dedup_key)
                    logger.debug("✓ Match : '%s' → '%s'", comp_name, compagnon.get_name())
                else:
                    logger.debug("✗ Non trouvé : '%s'", comp_name)

            # Phase 2 — warnings uniquement sur les noms originaux non matchés
            for original_name in data.original_names:
                original_normalized = self._normalize_aggressive(original_name)
                dedup_key = " ".join(sorted(original_normalized.split()))

                if dedup_key not in matched_keys:
                    warnings.append(MateWarning(
                        benevole_name=data.benevole_name,
                        comp_name=original_name,
                        message=f"Compagnon introuvable : '{original_name}'",
                    ))

        taux = (total_associations / total_tentatives * 100) if total_tentatives > 0 else 0.0
        logger.info(
            "Associations : %d/%d (%.1f%%)", total_associations, total_tentatives, taux
        )

        if warnings:
            logger.warning(
                "%d compagnon(s) non trouvé(s) — voir warnings dans le rapport d'import",
                len(warnings),
            )

        return warnings

    def extraire_noms_compagnons(self, liste_compagnons: Optional[str]) -> tuple[str, ...]:
        """Extrait les noms et génère les variantes inversées pour le matching.

        Returns:
            tuple immuable contenant les noms originaux **et** leurs variantes
            inversées (prénom-nom → nom-prénom), destiné à
            ``CompagnonData.compagnons_names``.
        """
        if not liste_compagnons or not liste_compagnons.strip():
            return ()

        separateurs = re.compile(r"[,;]")
        noms = [n.strip() for n in separateurs.split(liste_compagnons) if n.strip()]
        compagnons: list[str] = []

        for nom in noms:
            compagnons.append(nom)
            tokens = nom.split()
            if len(tokens) >= 2:
                # Variante inversée : "Jean Dupont" → "Dupont Jean"
                compagnons.append(" ".join([tokens[-1]] + tokens[:-1]))

        return tuple(compagnons)

    def extraire_noms_originaux(self, liste_compagnons: Optional[str]) -> tuple[str, ...]:
        """Extrait uniquement les noms originaux (sans variantes inversées).

        Returns:
            tuple immuable des noms tels que saisis, destiné à
            ``CompagnonData.original_names``.
        """
        if not liste_compagnons or not liste_compagnons.strip():
            return ()

        separateurs = re.compile(r"[,;]")
        return tuple(
            n.strip() for n in separateurs.split(liste_compagnons) if n.strip()
        )

    # =========================================================================
    # Méthodes privées — stratégies de matching
    # =========================================================================

    def _find_best_match(self, comp_normalized: str) -> Optional[Benevole]:
        """Orchestre les stratégies de matching et retourne le meilleur résultat.

        Args:
            comp_normalized: Nom du compagnon après normalisation agressive.

        Returns:
            Le :class:`~horizons_core.dataclass.benevole.Benevole` matchant,
            ou ``None`` si aucun candidat n'atteint ``min_confidence``.
        """
        # Stratégie 0 : exact (court-circuit immédiat)
        if comp_normalized in self._benevole_index:
            return self._benevole_index[comp_normalized]

        candidates: list[MatchCandidate] = []

        tokens = comp_normalized.split()
        if len(tokens) >= 2:
            candidates.extend(self._find_by_tokens(tokens))

        candidates.extend(self._find_by_levenshtein(comp_normalized))

        if not candidates:
            return None

        best = max(candidates, key=lambda c: c.score)
        if best.score >= self._min_confidence:
            logger.debug(
                "  Match method: %s, score: %.2f", best.method, best.score
            )
            return best.benevole

        return None

    def _find_by_tokens(self, tokens: list[str]) -> list[MatchCandidate]:
        """Stratégie token : score Jaccard sur l'intersection des tokens."""
        candidates: list[MatchCandidate] = []
        potential_benevoles: set[Benevole] = set()

        for token in tokens:
            if token in self._token_index:
                potential_benevoles.update(self._token_index[token])

        token_set = set(tokens)
        for benevole in potential_benevoles:
            benevole_name = self._normalize_aggressive(benevole.get_name())
            benevole_tokens = set(benevole_name.split())
            common_tokens = len(token_set & benevole_tokens)
            score = common_tokens / max(len(token_set), len(benevole_tokens))
            if score > 0.5:
                candidates.append(MatchCandidate(
                    benevole=benevole, score=score, method="token"
                ))

        return candidates

    def _find_by_levenshtein(self, comp_normalized: str) -> list[MatchCandidate]:
        """Stratégie Levenshtein : distance d'édition avec seuil adaptatif."""
        candidates: list[MatchCandidate] = []
        threshold = (
            self._levenshtein_threshold_short
            if len(comp_normalized) < 6
            else self._levenshtein_threshold_long
        )

        for name_normalized, benevole in self._benevole_index.items():
            distance = TextUtils._distance_levenshtein(comp_normalized, name_normalized)
            if distance < threshold:
                max_len = max(len(comp_normalized), len(name_normalized))
                score = 1.0 - (distance / max_len)
                candidates.append(MatchCandidate(
                    benevole=benevole,
                    score=score,
                    method=f"levenshtein(d={distance})",
                ))

        return candidates

    def _normalize_aggressive(self, name: str) -> str:
        """Normalise un nom pour le matching : minuscules, sans accent,
        sans ponctuation, espaces normalisés."""
        if not name:
            return ""
        normalized = TextUtils.nettoyer_texte(name)
        normalized = normalized.replace("-", " ").replace("'", " ")
        normalized = re.sub(r"[^a-z\s]", "", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized