from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .config import state_dir


HEARTBEAT_FILE = "hook-heartbeats.jsonl"
TOOL_EVENTS = {"PreToolUse", "PostToolUse"}


def record_hook(root: Path, event: str) -> None:
    path = state_dir(root) / "tmp" / HEARTBEAT_FILE
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        record = {"event": event, "timestamp": datetime.now(timezone.utc).isoformat()}
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    except OSError:
        pass


def observed_hooks(root: Path) -> dict[str, str]:
    path = state_dir(root) / "tmp" / HEARTBEAT_FILE
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}
    observed: dict[str, str] = {}
    for line in lines:
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        event = record.get("event")
        timestamp = record.get("timestamp")
        if isinstance(event, str) and isinstance(timestamp, str):
            observed[event] = timestamp
    return observed


def hook_status(observed: dict[str, str]) -> str:
    if TOOL_EVENTS.intersection(observed):
        return "observed"
    if observed:
        return "partially observed"
    return "not yet observed"
