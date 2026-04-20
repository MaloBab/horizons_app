import re
import unicodedata
from typing import Optional

class TextUtils:
    """Utilitaires pour le traitement de texte."""

    @staticmethod
    def nettoyer_texte(texte: Optional[str]) -> str:
        """
        Nettoie un texte en supprimant les accents, en le mettant en minuscule
        et en supprimant les espaces inutiles.

        Args:
            texte: Le texte à nettoyer.

        Returns:
            Le texte nettoyé.
        """
        if texte is None:
            return ""

        texte_minuscule = texte.lower()

        texte_normalise = unicodedata.normalize('NFD', texte_minuscule)
        texte_sans_accent = ''.join(
            char for char in texte_normalise
            if unicodedata.category(char) != 'Mn'
        )

        return re.sub(r'\s+', ' ', texte_sans_accent).strip()


    @staticmethod
    def _distance_levenshtein(s1: str, s2: str) -> int:
        """
        Calcule la distance de Levenshtein entre deux chaînes.

        Args:
            s1: Première chaîne.
            s2: Deuxième chaîne.

        Returns:
            La distance de Levenshtein.
        """
        if len(s1) < len(s2):
            return TextUtils._distance_levenshtein(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)

        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]
    
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Vérifie qu'un email a un format minimal valide (présence @ et .)."""
        return bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email.strip()))