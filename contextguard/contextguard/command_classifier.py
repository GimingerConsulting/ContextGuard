from __future__ import annotations

import shlex
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandDecision:
    action: str
    reason: str


def classify_command(command: str) -> CommandDecision:
    try:
        parts = shlex.split(command)
    except ValueError:
        return CommandDecision("allow", "Unable to parse shell safely; leaving command unchanged.")
    if not parts:
        return CommandDecision("allow", "Empty command.")
    joined = " ".join(parts)
    destructive = {"rm", "mv", "git reset", "git checkout", "git clean"}
    if any(joined.startswith(item) for item in destructive):
        return CommandDecision("allow", "Destructive or state-changing command is not rewritten.")
    first = parts[0]
    python_module = None
    if first.rsplit("/", 1)[-1] in {"python", "python3"} and len(parts) >= 3 and parts[1] == "-m":
        python_module = parts[2]
    if first == "cat" and len(parts) >= 2:
        return CommandDecision("capture", "Raw cat output can be large.")
    if first == "find":
        return CommandDecision("capture", "Recursive find output can be large.")
    if first == "ls" and any(flag in parts for flag in ("-R", "-laR", "-alR")):
        return CommandDecision("capture", "Recursive ls output can be large.")
    if parts[:2] == ["git", "diff"] and "--stat" not in parts:
        return CommandDecision("capture", "git diff can emit large patches.")
    if parts[:2] == ["git", "log"] and not any(p.startswith("--oneline") for p in parts):
        return CommandDecision("capture", "Verbose git log can be compacted.")
    if first in {"pytest", "ruff", "mypy", "npm", "pnpm", "yarn", "make"} or python_module in {"pytest", "ruff", "mypy"}:
        return CommandDecision("capture", "Validation command output is captured to preserve complete logs.")
    if first in {"grep", "rg"} and any(flag in parts for flag in ("-r", "-R", "--recursive")):
        return CommandDecision("capture", "Recursive search output can be large.")
    if first in {"tar", "unzip", "zipinfo"}:
        return CommandDecision("capture", "Archive listings can be large.")
    if any(part.endswith((".json", ".jsonl", ".csv", ".tsv", ".log", ".sql")) for part in parts[1:]):
        return CommandDecision("capture", "Structured or log output can be summarized compactly.")
    if any(part in joined for part in ("node_modules", "dist/", "build/", "coverage/")):
        return CommandDecision("guide", "Command targets generated or dependency output.")
    return CommandDecision("allow", "Command appears small or already scoped.")
