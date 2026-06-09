#!/usr/bin/env python3
from __future__ import annotations

from _bootstrap import read_event, write_event
from contextguard.config import state_dir
from contextguard.context_capsule import build_capsule
from contextguard.project import detect_project


event = read_event()
prompt = event.get("prompt") or event.get("user_prompt") or ""
info = detect_project()
if (state_dir(info.root) / "manifest.json").exists() and prompt:
    write_event({"additionalContext": build_capsule(info.root, prompt)})
else:
    write_event({})
