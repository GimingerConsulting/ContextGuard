from __future__ import annotations

import json
from pathlib import Path


def summarize(path: Path, limit: int = 5) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    result = {"file": path.as_posix(), "size": path.stat().st_size, "top_level_type": type(data).__name__}
    if isinstance(data, dict):
        result["keys"] = list(data.keys())[:50]
        result["sample"] = {k: type(v).__name__ for k, v in list(data.items())[:limit]}
    elif isinstance(data, list):
        result["records"] = len(data)
        result["sample_types"] = [type(v).__name__ for v in data[:limit]]
        if data and isinstance(data[0], dict):
            result["observed_keys"] = sorted({k for row in data[:100] if isinstance(row, dict) for k in row})[:100]
    return result
