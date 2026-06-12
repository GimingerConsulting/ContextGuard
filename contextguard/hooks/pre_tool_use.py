#!/usr/bin/env python3
from __future__ import annotations

from _bootstrap import read_event, write_event
from contextguard.command_classifier import classify_command
from contextguard.command_rewriter import rewrite_for_capture
from contextguard.config import state_dir
from contextguard.hook_diagnostics import record_hook
from contextguard.project import detect_project
import json
import os
from pathlib import Path


event = read_event()
tool = event.get("tool_name") or event.get("toolName")
tool_input = event.get("tool_input") or event.get("input") or {}
command = tool_input.get("command") or tool_input.get("cmd") or ""
if command:
    info = detect_project()
    if (state_dir(info.root) / "manifest.json").exists():
        record_hook(info.root, "PreToolUse")
    decision = classify_command(command)
    runner = Path(__file__).resolve().parents[1] / "scripts" / "contextguard"
    rewritten = rewrite_for_capture(command, runner)
    if os.environ.get("CONTEXTGUARD_BENCHMARK_METRICS") == "1":
        path = state_dir(info.root) / "tmp" / "hook-invocations.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"event": "PreToolUse", "tool": tool, "command": command, "rewrite_requested": bool(rewritten)}) + "\n")
    if rewritten:
        updated = dict(tool_input)
        if "command" in updated:
            updated["command"] = rewritten
        else:
            updated["cmd"] = rewritten
        write_event(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                    "updatedInput": updated,
                }
            }
        )
    else:
        write_event({})
else:
    write_event({})
