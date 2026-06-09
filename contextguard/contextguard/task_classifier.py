from __future__ import annotations

import re
from pathlib import Path

from .utils import iter_project_files, safe_relpath


def classify_task(root: Path, prompt: str) -> dict:
    terms = {t.lower() for t in re.findall(r"[A-Za-z_][A-Za-z0-9_.-]{2,}", prompt)}
    candidates = []
    for path in iter_project_files(root):
        rel = safe_relpath(path, root)
        low = rel.lower()
        score = sum(1 for term in terms if term in low)
        if score:
            candidates.append((score, rel))
    candidates.sort(reverse=True)
    confidence = "low" if not candidates else "medium" if candidates[0][0] < 2 else "high"
    return {
        "confidence": confidence,
        "likely_files": [rel for _, rel in candidates[:12]] if confidence != "low" else [],
        "recommended_scope": "Use metadata and symbol/range inspection first; expand only when evidence is insufficient.",
    }
