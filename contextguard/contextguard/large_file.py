from __future__ import annotations

from pathlib import Path

from . import summarize_csv, summarize_json, summarize_jsonl, summarize_log


def summarize_large_file(
    path: Path,
    contains: str | None = None,
    limit: int = 10,
    key: str | None = None,
    value: str | None = None,
    before: int = 0,
    after: int = 0,
    lines: str | None = None,
    records: str | None = None,
) -> dict:
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
        all_lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for number, line in enumerate(all_lines, start=1):
            if contains in line:
                start = max(1, number - before)
                end = min(len(all_lines), number + after)
                matches.append(
                    {
                        "line": number,
                        "text": line.rstrip()[:500],
                        "context": all_lines[start - 1 : end] if before or after else [],
                    }
                )
                if len(matches) >= limit:
                    break
        result["matches"] = matches
    if key:
        result["filter_key"] = key
    if value:
        result["filter_value"] = value
    if lines:
        start, _, end = lines.partition(":")
        start_i = max(1, int(start or "1"))
        end_i = int(end or str(start_i + limit - 1))
        all_lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        result["selected_lines"] = [
            {"line": index, "text": text[:500]}
            for index, text in enumerate(all_lines[start_i - 1 : end_i], start=start_i)
        ]
    if records:
        result["selected_records"] = records
    return result
