#!/usr/bin/env python3
from __future__ import annotations

from _bootstrap import read_event, write_event
from contextguard.output_compactor import compact_output


event = read_event()
output = event.get("output") or event.get("result") or ""
if isinstance(output, str) and len(output.encode()) > 64_000:
    compact = compact_output(output, "")
    write_event({"replacementOutput": "ContextGuard compacted large tool output:\n" + "\n".join(compact["summary_lines"])})
else:
    write_event({})
