#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone

from _bootstrap import read_event, write_event
from contextguard.config import state_dir
from contextguard.output_compactor import compact_output
from contextguard.project import detect_project


event = read_event()
output = event.get("output") or event.get("result") or ""
if isinstance(output, str) and len(output.encode()) > 64_000:
    info = detect_project()
    tmp = state_dir(info.root) / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = tmp / f"tool-output-{stamp}.txt"
    summary_path = tmp / f"tool-output-{stamp}.summary.json"
    output_path.write_text(output, encoding="utf-8", errors="replace")
    compact = compact_output(output, "")
    compact["full_output_path"] = output_path.as_posix()
    summary_path.write_text(json.dumps(compact, indent=2) + "\n", encoding="utf-8")
    write_event(
        {
            "replacementOutput": (
                "ContextGuard compacted large tool output:\n"
                + (f"tests: {compact['test_summary']}\n" if compact.get("test_summary") else "")
                + "\n".join(compact["errors"] + compact["warnings"])
                + (f"\nstack_trace:\n{compact['stack_traces'][0]}" if compact.get("stack_traces") else "")
                + f"\nfull_output: {output_path}\nsummary: {summary_path}"
            )
        }
    )
else:
    write_event({})
