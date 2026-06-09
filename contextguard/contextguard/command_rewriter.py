from __future__ import annotations

import shlex

from .command_classifier import classify_command


def rewrite_for_capture(command: str) -> str | None:
    decision = classify_command(command)
    if decision.action != "capture":
        return None
    return " ".join(["contextguard", "capture", "--", "sh", "-c", shlex.quote(command)])
