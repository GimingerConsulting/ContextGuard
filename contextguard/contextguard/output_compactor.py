from __future__ import annotations

from .utils import extract_error_lines


def compact_output(stdout: str, stderr: str, *, limit: int = 24) -> dict:
    combined = "\n".join(part for part in (stdout, stderr) if part)
    lines = combined.splitlines()
    errors = extract_error_lines(combined)
    head = lines[: min(8, len(lines))]
    tail = lines[-8:] if len(lines) > 8 else []
    selected = []
    for line in head + errors + tail:
        if line not in selected:
            selected.append(line)
        if len(selected) >= limit:
            break
    return {
        "line_count": len(lines),
        "stdout_bytes": len(stdout.encode()),
        "stderr_bytes": len(stderr.encode()),
        "errors": errors[:10],
        "summary_lines": selected,
    }
