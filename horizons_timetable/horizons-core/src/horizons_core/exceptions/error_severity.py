from enum import Enum

class ErrorSeverity(Enum):
    """Niveau de sévérité des erreurs de parsing."""
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
