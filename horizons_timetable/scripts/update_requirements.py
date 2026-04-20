#!/usr/bin/env python3
"""
Met à jour les lignes horizons-core et parsing-poste dans backend/requirements.txt
avec les versions courantes lues depuis les pyproject.toml.
"""
import os
import re
from pathlib import Path


REPO      = os.environ["GITHUB_REPO"]
CORE_VER  = os.environ["CORE_VERSION"]
PARSE_VER = os.environ["PARSING_VERSION"]

REQ_PATH  = Path("requirements.txt")
content   = REQ_PATH.read_text(encoding="utf-8")

BASE_URL  = f"git+https://${{GITHUB_TOKEN}}@github.com/{REPO}.git"

# Remplace ou ajoute les deux lignes
def replace_or_add(text: str, package: str, version: str, subdir: str) -> str:
    new_line = (
        f"{package} @ {BASE_URL}"
        f"@v-{'core' if 'core' in subdir else 'parsing'}-{version}"
        f"#subdirectory={subdir}"
    )
    pattern = rf"^{re.escape(package)}\s*@.*$"
    if re.search(pattern, text, re.MULTILINE):
        return re.sub(pattern, new_line, text, flags=re.MULTILINE)
    return new_line + "\n" + text


content = replace_or_add(content, "horizons-core", CORE_VER,  "horizons-core")
content = replace_or_add(content, "parsing-poste", PARSE_VER, "parsing-poste")

REQ_PATH.write_text(content, encoding="utf-8")
print(f"✅ requirements.txt mis à jour — core@{CORE_VER} parsing@{PARSE_VER}")


# **Résumé du flux complet une fois en place**

# git push origin main  (avec modifs dans horizons-core/)
#         ↓
# version-core.yml     → bump 0.1.0 → 0.1.1
#                      → commit "chore(horizons-core): bump to v0.1.1 [skip ci]"
#                      → tag v-core-0.1.1
#         ↓
# sync-backend.yml     → lit les versions courantes
#                      → met à jour backend/requirements.txt
#                      → commit "chore(backend): sync deps core@0.1.1 ..."
#         ↓
# (quand tu auras choisi ta plateforme)
# deploy.yml           → redéploie le backend automatiquement