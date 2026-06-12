from __future__ import annotations

import shlex
import sys
from pathlib import Path

from .config import state_dir


def runner_path(root: Path) -> Path:
    return state_dir(root) / "bin" / "contextguard"


def install_project_runner(root: Path) -> Path:
    path = runner_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    package_root = Path(__file__).resolve().parents[1]
    bootstrap = (
        "import sys; "
        f"sys.path.insert(0, {package_root.as_posix()!r}); "
        "from contextguard.cli import main; "
        "raise SystemExit(main())"
    )
    content = (
        "#!/bin/sh\n"
        f"exec {shlex.quote(sys.executable)} -c {shlex.quote(bootstrap)} \"$@\"\n"
    )
    if not path.exists() or path.read_text(encoding="utf-8") != content:
        path.write_text(content, encoding="utf-8")
    path.chmod(0o755)
    return path


def project_runner_ready(root: Path) -> bool:
    path = runner_path(root)
    return path.is_file() and bool(path.stat().st_mode & 0o111)
