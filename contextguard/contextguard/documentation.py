from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from .config import MANAGED_BEGIN, MANAGED_END
from .output_policy import render_policy
from .project import ProjectInfo
from .repo_map import detect_repo_facts


def _backup(path: Path) -> Path | None:
    if not path.exists():
        return None
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = path.with_suffix(path.suffix + f".contextguard-backup-{stamp}")
    shutil.copy2(path, backup)
    return backup


def replace_managed_section(path: Path, title: str, body: str) -> bool:
    section = f"{MANAGED_BEGIN}\n{body.rstrip()}\n{MANAGED_END}\n"
    if path.exists():
        current = path.read_text(encoding="utf-8")
        if MANAGED_BEGIN in current and MANAGED_END in current:
            before = current.split(MANAGED_BEGIN, 1)[0]
            after = current.split(MANAGED_END, 1)[1]
            next_text = before + section + after.lstrip("\n")
        else:
            next_text = current.rstrip() + f"\n\n## {title}\n\n" + section
    else:
        next_text = f"# {title}\n\n{section}"
    if path.exists() and path.read_text(encoding="utf-8") == next_text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    _backup(path)
    path.write_text(next_text, encoding="utf-8")
    return True


def update_gitignore(root: Path) -> bool:
    path = root / ".gitignore"
    additions = [
        ".contextguard/index.sqlite",
        ".contextguard/cache/",
        ".contextguard/sessions/",
        ".contextguard/reports/",
        ".contextguard/tmp/",
    ]
    existing = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    missing = [line for line in additions if line not in existing]
    if not missing:
        return False
    path.write_text("\n".join(existing + missing).strip() + "\n", encoding="utf-8")
    return True


def render_agents(info: ProjectInfo) -> str:
    return render_policy(info.kind)


def render_architecture(root: Path) -> str:
    facts = detect_repo_facts(root)
    return f"""## System Purpose

This document is factual project guidance maintained by ContextGuard. It should be expanded only from verified repository evidence.

## Major Components

- Detected languages: {", ".join(facts["languages"]) or "none yet"}.
- Configuration files: {", ".join(facts["config_files"]) or "none detected"}.

## Entry Points

{", ".join(facts["entry_points"]) or "No entry points detected yet."}

## Data Flow

No data flow has been inferred beyond repository metadata.

## Storage

ContextGuard stores local state in `.contextguard/`.

## External Services

No external service usage was detected by ContextGuard.

## Tests

{", ".join(facts["tests"]) or "No test command detected yet."}

## Dependency Boundaries

Generated and vendor outputs should not be used as primary context.

## Generated Outputs

Common generated directories are excluded from ContextGuard indexing.

## Known Constraints

ContextGuard guidance is deterministic and should be corrected when repository facts change.
"""


def render_current_state(info: ProjectInfo) -> str:
    return f"""- Current objective: keep Codex context focused while preserving correctness.
- Verified current state: project classified as `{info.kind}`.
- Relevant files: AGENTS.md, docs/ARCHITECTURE.md, docs/CURRENT_STATE.md, .contextguard/manifest.json.
- Active decisions: use Adaptive Maximum Efficiency with automatic context escalation.
- Known blockers: none recorded.
- Completed validation: ContextGuard initialization completed locally.
- Next concrete action: use focused search and targeted file inspection for the next task.
- Rejected paths: do not read every file or paste large raw outputs by default.
"""


def write_managed_docs(info: ProjectInfo) -> list[str]:
    root = info.root
    changed = []
    if replace_managed_section(root / "AGENTS.md", "Project Instructions", render_agents(info)):
        changed.append("AGENTS.md")
    if replace_managed_section(root / "docs" / "ARCHITECTURE.md", "Architecture", render_architecture(root)):
        changed.append("docs/ARCHITECTURE.md")
    if replace_managed_section(root / "docs" / "CURRENT_STATE.md", "Current State", render_current_state(info)):
        changed.append("docs/CURRENT_STATE.md")
    if update_gitignore(root):
        changed.append(".gitignore")
    return changed
