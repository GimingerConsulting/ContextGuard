#!/usr/bin/env python3
from __future__ import annotations

from _bootstrap import read_event, write_event
from contextguard.config import state_dir
from contextguard.hook_diagnostics import record_hook
from contextguard.onboarding import initialize_project
from contextguard.project import detect_project
from contextguard.session_state import reset_session_state


event = read_event()
info = detect_project()
if (state_dir(info.root) / "manifest.json").exists():
    record_hook(info.root, "SessionStart")
    reset_session_state(info.root)
    write_event({})
else:
    try:
        result = initialize_project(info.root)
        record_hook(result.project.root, "SessionStart")
        reset_session_state(result.project.root)
        message = "ContextGuard initialized automatically for this project. Continue with the user's task normally."
    except Exception as exc:
        message = f"ContextGuard automatic setup failed: {exc}. Run `$contextguard-setup` to diagnose and retry."
    write_event({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": message}})
