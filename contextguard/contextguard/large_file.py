from __future__ import annotations

from pathlib import Path

from . import summarize_csv, summarize_json, summarize_jsonl, summarize_log


def summarize_large_file(path: Path, contains: str | None = None, limit: int = 10) -> dict:
    suffix = path.suffix.lower()
    if suffix == ".json":
        result = summarize_json.summarize(path, limit=limit)
    elif suffix == ".jsonl":
        result = summarize_jsonl.summarize(path, limit=limit)
    elif suffix in {".csv", ".tsv"}:
        result = summarize_csv.summarize(path, delimiter="\t" if suffix == ".tsv" else None, limit=limit)
    else:
        result = summarize_log.summarize(path, limit=limit)
    if contains:
        matches = []
        with path.open(encoding="utf-8", errors="replace") as handle:
            for number, line in enumerate(handle, start=1):
                if contains in line:
                    matches.append({"line": number, "text": line.rstrip()[:500]})
                    if len(matches) >= limit:
                        break
        result["matches"] = matches
    return result
