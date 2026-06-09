#!/usr/bin/env python3
from __future__ import annotations

from _bootstrap import read_event, write_event
from contextguard.config import state_dir
from contextguard.project import detect_project


event = read_event()
info = detect_project()
if (state_dir(info.root) / "manifest.json").exists():
    message = (
        "ContextGuard active. Use targeted symbol and range inspection first. "
        "Large output protection is active. Optimization: Adaptive Maximum Savings. "
        "Automatically expand context when evidence is insufficient."
    )
else:
    message = "ContextGuard available but this project is not initialized. Run `$contextguard-init` once to enable local indexing."
write_event({"additionalContext": message, "event": event.get("hook_event_name", "SessionStart")})
