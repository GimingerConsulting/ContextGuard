from __future__ import annotations

import json
import re
import time
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


PY_SYMBOL_RE = re.compile(r"^\s*(def|class)\s+([A-Za-z_][A-Za-z0-9_]*)")
JS_SYMBOL_RE = re.compile(r"^\s*(?:export\s+)?(?:async\s+)?(?:function|class)\s+([A-Za-z_$][A-Za-z0-9_$]*)")
IMPORT_RE = re.compile(r"^\s*(?:from\s+([A-Za-z0-9_.$/-]+)\s+import|import\s+([A-Za-z0-9_.$/-]+))")


def _index_text_metadata(conn, root: Path, path: Path, rel: str, language: str | None) -> None:
    if path.stat().st_size > 512_000 or language not in {"Python", "JavaScript", "TypeScript"}:
        return
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return
    conn.execute("delete from symbols where path = ?", (rel,))
    conn.execute("delete from imports where path = ?", (rel,))
    for number, line in enumerate(lines, start=1):
        if language == "Python":
            symbol = PY_SYMBOL_RE.match(line)
            if symbol:
                conn.execute(
                    "insert or ignore into symbols(path,name,kind,line) values(?,?,?,?)",
                    (rel, symbol.group(2), symbol.group(1), number),
                )
            imported = IMPORT_RE.match(line)
            if imported:
                conn.execute(
                    "insert or ignore into imports(path,target,line) values(?,?,?)",
                    (rel, imported.group(1) or imported.group(2), number),
                )
        else:
            symbol = JS_SYMBOL_RE.match(line)
            if symbol:
                kind = "class" if "class" in line else "function"
                conn.execute(
                    "insert or ignore into symbols(path,name,kind,line) values(?,?,?,?)",
                    (rel, symbol.group(1), kind, number),
                )


def _index_package_metadata(conn, root: Path) -> None:
    package_json = root / "package.json"
    if package_json.exists():
        try:
            payload = json.loads(package_json.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
        scripts = payload.get("scripts", {}) if isinstance(payload, dict) else {}
        if isinstance(scripts, dict):
            for name, command in scripts.items():
                if isinstance(name, str) and isinstance(command, str):
                    conn.execute(
                        "insert or replace into package_scripts(manager,name,command) values(?,?,?)",
                        ("npm", name, command),
                    )


def refresh_index(root: Path) -> dict[str, int]:
    started = time.time()
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
        language = LANG_BY_SUFFIX.get(path.suffix.lower())
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
                language,
                int(is_large),
                int(is_generated(rel)),
            ),
        )
        if rel.startswith("tests/") or "/tests/" in rel or path.name.startswith("test_") or path.name.endswith(".test.ts"):
            conn.execute("insert or replace into tests(path, kind) values(?, ?)", (rel, "test"))
        _index_text_metadata(conn, root, path, rel, language)
    _index_package_metadata(conn, root)
    duration_ms = int((time.time() - started) * 1000)
    conn.execute("insert or replace into project(key,value) values('last_refresh', datetime('now'))")
    conn.execute(
        "insert into metrics(key, value) values('index_refresh_duration_ms', ?) "
        "on conflict(key) do update set value = excluded.value",
        (duration_ms,),
    )
    conn.commit()
    (state_dir(root) / "fingerprints.json").write_text(
        json.dumps({"files_indexed": total, "large_files": large}, indent=2) + "\n",
        encoding="utf-8",
    )
    return {"files_indexed": total, "files_changed": changed, "large_files": large, "duration_ms": duration_ms}
