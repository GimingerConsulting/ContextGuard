from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from .config import database_path
from .utils import iter_project_files, safe_relpath, search_paths_for_terms


def classify_task(root: Path, prompt: str) -> dict:
    terms = {t.lower() for t in re.findall(r"[A-Za-z_][A-Za-z0-9_.-]{2,}", prompt)}
    candidates = []
    tests = []
    symbols = []
    for path in iter_project_files(root):
        rel = safe_relpath(path, root)
        low = rel.lower()
        score = sum(1 for term in terms if term in low)
        if score:
            candidates.append((score, rel))
    for rel in search_paths_for_terms(root, terms):
        candidates.append((2, rel))
    db_path = database_path(root)
    if db_path.exists():
        try:
            conn = sqlite3.connect(db_path)
            for term in terms:
                like = f"%{term}%"
                for name, kind, path, line in conn.execute(
                    "select name, kind, path, line from symbols where lower(name) like ? limit 20",
                    (like,),
                ):
                    symbols.append({"name": name, "kind": kind, "path": path, "line": line})
                    candidates.append((3, path))
                for path, kind in conn.execute("select path, kind from tests where lower(path) like ? limit 20", (like,)):
                    tests.append(path)
        except Exception:
            pass
    candidates.sort(reverse=True)
    confidence = "low" if not candidates else "medium" if candidates[0][0] < 2 else "high"
    likely_files = []
    for _, rel in candidates:
        if rel not in likely_files:
            likely_files.append(rel)
    return {
        "confidence": confidence,
        "likely_files": likely_files[:12] if confidence != "low" else [],
        "likely_symbols": symbols[:12] if confidence != "low" else [],
        "relevant_tests": tests[:8] if confidence != "low" else [],
        "recommended_scope": "Use metadata and symbol/range inspection first; expand only when evidence is insufficient.",
    }
