from __future__ import annotations

from pathlib import Path

from .utils import extract_error_lines


def summarize(path: Path, limit: int = 10) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    return {
        "file": path.as_posix(),
        "size": path.stat().st_size,
        "line_count": len(lines),
        "error_signatures": extract_error_lines(text, limit=limit),
        "tail": lines[-limit:],
    }
