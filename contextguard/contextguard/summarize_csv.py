from __future__ import annotations

import csv
from pathlib import Path


def summarize(path: Path, delimiter: str | None = None, limit: int = 5) -> dict:
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        sample = handle.read(4096)
        handle.seek(0)
        dialect = csv.Sniffer().sniff(sample) if delimiter is None and sample else csv.excel
        if delimiter:
            dialect.delimiter = delimiter
        reader = csv.DictReader(handle, dialect=dialect)
        rows = []
        count = 0
        nulls = {name: 0 for name in (reader.fieldnames or [])}
        for row in reader:
            count += 1
            if len(rows) < limit:
                rows.append(row)
            for key, value in row.items():
                if value in (None, ""):
                    nulls[key] = nulls.get(key, 0) + 1
    return {"file": path.as_posix(), "records": count, "columns": reader.fieldnames or [], "null_counts": nulls, "samples": rows}
