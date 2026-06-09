from __future__ import annotations

from pathlib import Path


STATE_DIR = ".contextguard"
MANAGED_BEGIN = "<!-- BEGIN CONTEXTGUARD MANAGED SECTION -->"
MANAGED_END = "<!-- END CONTEXTGUARD MANAGED SECTION -->"


def state_dir(root: Path) -> Path:
    return root / STATE_DIR


def database_path(root: Path) -> Path:
    return state_dir(root) / "index.sqlite"
