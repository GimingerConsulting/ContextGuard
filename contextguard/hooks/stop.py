#!/usr/bin/env python3
from __future__ import annotations

from _bootstrap import read_event, write_event
from contextguard.index import refresh_index
from contextguard.project import detect_project


event = read_event()
if event.get("stop_hook_active"):
    write_event({})
else:
    info = detect_project()
    try:
        refresh_index(info.root)
    except Exception:
        pass
    write_event({})
