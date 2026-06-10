#!/usr/bin/env python3
from __future__ import annotations

from _bootstrap import read_event, write_event
from contextguard.config import state_dir
from contextguard.project import detect_project


event = read_event()
info = detect_project()
if (state_dir(info.root) / "manifest.json").exists():
    write_event({})
else:
    message = "ContextGuard available but this project is not initialized. Run `$contextguard-init` once to enable local indexing."
    write_event({"additionalContext": message, "event": event.get("hook_event_name", "SessionStart")})
