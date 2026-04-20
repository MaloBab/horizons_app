#!/usr/bin/env python3
"""
Bumpe automatiquement la version patch dans un pyproject.toml.
Usage : python scripts/bump_version.py horizons-core/pyproject.toml
"""
import sys
import re
from pathlib import Path


def bump_patch(filepath: str) -> str:
    """Lit le pyproject.toml, incrémente le patch, écrit et retourne la nouvelle version."""
    path = Path(filepath)
    content = path.read_text(encoding="utf-8")

    match = re.search(r'^version\s*=\s*"(\d+)\.(\d+)\.(\d+)"', content, re.MULTILINE)
    if not match:
        print(f"❌ Version introuvable dans {filepath}")
        sys.exit(1)

    major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))
    new_version = f"{major}.{minor}.{patch + 1}"

    new_content = content[:match.start()] + f'version = "{new_version}"' + content[match.end():]
    path.write_text(new_content, encoding="utf-8")

    print(new_version)  # stdout capturé par GitHub Actions
    return new_version


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: bump_version.py <path/to/pyproject.toml>")
        sys.exit(1)
    bump_patch(sys.argv[1])