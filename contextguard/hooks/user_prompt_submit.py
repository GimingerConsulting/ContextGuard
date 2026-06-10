#!/usr/bin/env python3
from __future__ import annotations

from _bootstrap import read_event, write_event
from contextguard.config import state_dir
from contextguard.context_capsule import build_capsule, build_session_capsule
from contextguard.database import connect, increment
from contextguard.project import detect_project


event = read_event()
prompt = event.get("prompt") or event.get("user_prompt") or ""
info = detect_project()
if (state_dir(info.root) / "manifest.json").exists() and prompt:
    parts = [part for part in (build_session_capsule(info.root), build_capsule(info.root, prompt, token_limit=300)) if part]
    context = "\n".join(parts)
    conn = connect(state_dir(info.root) / "index.sqlite")
    increment(conn, "context_bytes_added", len(context.encode()))
    write_event(
        {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": context,
            }
        }
    )
else:
    write_event({})
