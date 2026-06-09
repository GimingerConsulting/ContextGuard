from __future__ import annotations

import json
from pathlib import Path

from .config import database_path, state_dir
from .database import connect
from .utils import is_binary, iter_project_files, safe_relpath, sha256_file


LANG_BY_SUFFIX = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".json": "JSON",
    ".md": "Markdown",
    ".csv": "CSV",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".sql": "SQL",
}


def file_kind(path: Path) -> str:
    if is_binary(path):
        return "binary"
    return "text"


def is_generated(rel: str) -> bool:
    parts = set(rel.split("/"))
    return bool(parts & {"node_modules", "dist", "build", "coverage", "vendor"})


def refresh_index(root: Path) -> dict[str, int]:
    conn = connect(database_path(root))
    changed = 0
    total = 0
    large = 0
    for path in iter_project_files(root):
        rel = safe_relpath(path, root)
        stat = path.stat()
        total += 1
        is_large = stat.st_size > 512_000
        large += int(is_large)
        digest = sha256_file(path) if stat.st_size <= 20_000_000 else f"large:{stat.st_size}:{stat.st_mtime}"
        existing = conn.execute("select size, mtime, sha256 from files where path = ?", (rel,)).fetchone()
        if existing == (stat.st_size, stat.st_mtime, digest):
            continue
        changed += 1
        conn.execute(
            "insert or replace into files(path,size,mtime,sha256,kind,language,is_large,is_generated) "
            "values(?,?,?,?,?,?,?,?)",
            (
                rel,
                stat.st_size,
                stat.st_mtime,
                digest,
                file_kind(path),
                LANG_BY_SUFFIX.get(path.suffix.lower()),
                int(is_large),
                int(is_generated(rel)),
            ),
        )
    conn.execute("insert or replace into project(key,value) values('last_refresh', datetime('now'))")
    conn.commit()
    (state_dir(root) / "fingerprints.json").write_text(
        json.dumps({"files_indexed": total, "large_files": large}, indent=2) + "\n",
        encoding="utf-8",
    )
    return {"files_indexed": total, "files_changed": changed, "large_files": large}
