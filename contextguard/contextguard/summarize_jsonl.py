from __future__ import annotations

import json
from pathlib import Path


def summarize(path: Path, limit: int = 5) -> dict:
    keys: set[str] = set()
    samples = []
    count = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        count += 1
        if len(samples) < limit:
            samples.append(line[:300])
        try:
            value = json.loads(line)
        except Exception:
            continue
        if isinstance(value, dict):
            keys.update(value)
    return {"file": path.as_posix(), "records": count, "observed_keys": sorted(keys)[:100], "samples": samples}
