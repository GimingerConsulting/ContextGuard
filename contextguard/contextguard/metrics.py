from __future__ import annotations

from pathlib import Path

from .config import database_path
from .database import connect


def report(root: Path) -> dict:
    conn = connect(database_path(root))
    metrics = dict(conn.execute("select key, value from metrics").fetchall())
    files = conn.execute("select count(*) from files").fetchone()[0]
    commands = conn.execute("select count(*), coalesce(sum(stdout_bytes + stderr_bytes),0) from commands").fetchone()
    raw = int(commands[1] or 0)
    estimated_overhead = int(metrics.get("context_bytes_added", 0))
    return {
        "files_indexed": files,
        "commands_intercepted": int(commands[0] or 0),
        "raw_output_bytes": raw,
        "compact_output_bytes": int(metrics.get("compact_output_bytes", 0)),
        "large_files_summarized": int(metrics.get("large_files_summarized", 0)),
        "estimated_tokens_avoided": max(0, raw // 4 - estimated_overhead // 4),
        "estimated_contextguard_overhead_tokens": estimated_overhead // 4,
    }
