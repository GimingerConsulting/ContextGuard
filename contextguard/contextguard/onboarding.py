from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path

from .config import database_path, state_dir
from .database import connect
from .documentation import render_agents, write_managed_docs
from .index import refresh_index
from .output_policy import POLICY_NAME
from .project import ProjectInfo, detect_project
from .repo_map import detect_repo_facts


@dataclass(frozen=True)
class InitializationResult:
    project: ProjectInfo
    already_initialized: bool
    files_indexed: int
    changed_docs: tuple[str, ...]


def initialize_project(path: Path | None = None) -> InitializationResult:
    info = detect_project(path.resolve() if path else None)
    manifest_path = state_dir(info.root) / "manifest.json"
    already_initialized = manifest_path.exists()
    if already_initialized:
        try:
            previous_kind = json.loads(manifest_path.read_text(encoding="utf-8")).get("project_kind")
        except (OSError, json.JSONDecodeError):
            previous_kind = None
        if isinstance(previous_kind, str) and previous_kind:
            info = replace(info, kind=previous_kind)

    for name in ("cache", "sessions", "reports", "tmp"):
        (state_dir(info.root) / name).mkdir(parents=True, exist_ok=True)

    index_stats = refresh_index(info.root)
    (state_dir(info.root) / "repo_map.json").write_text(
        json.dumps(detect_repo_facts(info.root), indent=2) + "\n",
        encoding="utf-8",
    )
    changed_docs = tuple(write_managed_docs(info))
    conn = connect(database_path(info.root))
    conn.execute(
        "insert or replace into metrics(key, value) values('managed_policy_bytes', ?)",
        (len(render_agents(info).encode()),),
    )
    conn.commit()
    manifest = {
        "initialized_at": datetime.now(timezone.utc).isoformat(),
        "project_root": info.root.as_posix(),
        "project_kind": info.kind,
        "policy": POLICY_NAME,
        "database": database_path(info.root).as_posix(),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return InitializationResult(
        project=info,
        already_initialized=already_initialized,
        files_indexed=int(index_stats["files_indexed"]),
        changed_docs=changed_docs,
    )
