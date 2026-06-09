from __future__ import annotations

import json
from pathlib import Path

from .config import state_dir


def read_fingerprints(root: Path) -> dict:
    path = state_dir(root) / "fingerprints.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
