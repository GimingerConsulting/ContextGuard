from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectInfo:
    root: Path
    kind: str
    is_git: bool
    is_monorepo: bool


def find_git_root(start: Path | None = None) -> Path | None:
    cwd = (start or Path.cwd()).resolve()
    try:
        output = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        return None
    return Path(output).resolve() if output else None


def detect_project_root(start: Path | None = None) -> Path:
    return find_git_root(start) or (start or Path.cwd()).resolve()


def detect_project(start: Path | None = None) -> ProjectInfo:
    root = detect_project_root(start)
    files = [p for p in root.iterdir() if p.name not in {".git", ".contextguard"}]
    is_git = (root / ".git").exists()
    package_markers = list(root.glob("*/package.json")) + list(root.glob("*/pyproject.toml"))
    workspace_markers = [
        root / "pnpm-workspace.yaml",
        root / "lerna.json",
        root / "turbo.json",
        root / "nx.json",
    ]
    is_monorepo = any(p.exists() for p in workspace_markers) or len(package_markers) > 1
    if not files:
        kind = "empty"
    elif not is_git and len(files) < 5:
        kind = "new-partial"
    elif is_monorepo:
        kind = "monorepo"
    else:
        kind = "existing"
    return ProjectInfo(root=root, kind=kind, is_git=is_git, is_monorepo=is_monorepo)
