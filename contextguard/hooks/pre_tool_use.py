#!/usr/bin/env python3
from __future__ import annotations

from _bootstrap import read_event, write_event
from contextguard.command_classifier import classify_command
from contextguard.command_rewriter import rewrite_for_capture


event = read_event()
tool = event.get("tool_name") or event.get("toolName")
tool_input = event.get("tool_input") or event.get("input") or {}
command = tool_input.get("command") or tool_input.get("cmd") or ""
if tool in {"Bash", "Shell", "functions.exec_command"} and command:
    decision = classify_command(command)
    rewritten = rewrite_for_capture(command)
    if rewritten:
        updated = dict(tool_input)
        if "command" in updated:
            updated["command"] = rewritten
        else:
            updated["cmd"] = rewritten
        write_event({"permissionDecision": "allow", "updatedInput": updated, "message": decision.reason})
    else:
        write_event({"permissionDecision": "allow", "message": decision.reason})
else:
    write_event({})
