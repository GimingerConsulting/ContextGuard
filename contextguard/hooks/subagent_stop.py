#!/usr/bin/env python3
from __future__ import annotations

from _bootstrap import read_event, write_event
from contextguard.config import state_dir
from contextguard.hook_diagnostics import record_hook
from contextguard.project import detect_project
from contextguard.session_state import record_routing_event


event = read_event()
info = detect_project()
agent_type = event.get("agent_type") or event.get("agentType") or event.get("type") or ""
model = event.get("model") or ""
thread_id = event.get("thread_id") or event.get("threadId") or ""
status = event.get("status") or "completed"
if (state_dir(info.root) / "manifest.json").exists():
    record_hook(info.root, "SubagentStop")
    record_routing_event(
        info.root,
        {
            "event": "stop",
            "agent_type": agent_type,
            "model": model,
            "thread_id": thread_id,
            "status": status,
        },
    )
write_event({})
