from __future__ import annotations

import shlex
from pathlib import Path

from .command_classifier import classify_command


def rewrite_for_capture(command: str, runner: Path | None = None) -> str | None:
    decision = classify_command(command)
    if decision.action != "capture":
        return None
    executable = runner.as_posix() if runner is not None else "contextguard"
    return " ".join([shlex.quote(executable), "capture", "--", "sh", "-c", shlex.quote(command)])
