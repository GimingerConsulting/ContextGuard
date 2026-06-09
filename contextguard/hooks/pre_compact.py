#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone

from _bootstrap import read_event, write_event
from contextguard.config import state_dir
from contextguard.project import detect_project


event = read_event()
info = detect_project()
session_dir = state_dir(info.root) / "sessions"
session_dir.mkdir(parents=True, exist_ok=True)
(session_dir / "pre_compact.json").write_text(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "event": event}, indent=2), encoding="utf-8")
write_event({"additionalContext": "ContextGuard persisted compact deterministic session facts locally."})
