# app/services/task_manager.py
#
# Gestionnaire de tâches en mémoire (pas de Redis requis).
# Stocke la progression des tâches longues (ex: algorithme génétique).
# Les tâches expirent automatiquement après TTL_SECONDS.
#
import uuid
import time
import threading
from typing import Optional

TTL_SECONDS = 60 * 60 * 6  # 6 heures

# ── Stockage en mémoire ───────────────────────────────────────────────────────
# { task_id: { "data": {...}, "expires_at": float } }
_store: dict[str, dict] = {}
_lock = threading.Lock()


# ── Nettoyage périodique des tâches expirées ─────────────────────────────────

def _cleanup():
    now = time.monotonic()
    with _lock:
        expired = [tid for tid, v in _store.items() if v["expires_at"] < now]
        for tid in expired:
            del _store[tid]


# ── API publique ──────────────────────────────────────────────────────────────

def create_task() -> str:
    """Crée une nouvelle tâche et retourne son ID."""
    task_id = str(uuid.uuid4())
    with _lock:
        _store[task_id] = {
            "data": {
                "status":      "pending",
                "pct":         0,
                "msg":         "En attente…",
                "assignments": None,
                "error":       None,
            },
            "expires_at": time.monotonic() + TTL_SECONDS,
        }
    return task_id


def update_task(task_id: str, **kwargs):
    """Met à jour les champs d'une tâche existante."""
    with _lock:
        entry = _store.get(task_id)
        if entry is None:
            return
        entry["data"].update(kwargs)
        # Repousse l'expiration à chaque mise à jour
        entry["expires_at"] = time.monotonic() + TTL_SECONDS


def get_task(task_id: str) -> Optional[dict]:
    """Retourne les données d'une tâche, ou None si introuvable/expirée."""
    _cleanup()
    with _lock:
        entry = _store.get(task_id)
        if entry is None:
            return None
        if entry["expires_at"] < time.monotonic():
            del _store[task_id]
            return None
        return dict(entry["data"])