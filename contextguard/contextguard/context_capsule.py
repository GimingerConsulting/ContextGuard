from __future__ import annotations

import json
from pathlib import Path

from .config import state_dir
from .task_classifier import classify_task
from .utils import estimate_tokens


def build_capsule(root: Path, prompt: str, token_limit: int = 400) -> str:
    result = classify_task(root, prompt)
    if result["confidence"] == "low":
        text = (
            "ContextGuard task capsule: low classification confidence. "
            "Start with targeted search, symbol/range inspection and automatic context escalation when needed."
        )
    else:
        files = ", ".join(result["likely_files"][:4]) or "none"
        symbols = ", ".join(
            f"{item['name']}@{item['path']}:{item['line']}"
            for item in result.get("likely_symbols", [])[:2]
        ) or "none"
        tests = ", ".join(result.get("relevant_tests", [])[:3]) or "none"
        text = (
            "ContextGuard capsule: "
            f"confidence={result['confidence']}; "
            f"files={files}; "
            f"symbols={symbols}; "
            f"tests={tests}; "
            "start scoped; expand if needed."
        )
    while estimate_tokens(text) > token_limit and "\n-" in text:
        text = "\n".join(text.splitlines()[:-1])
    return text


SESSION_FIELDS = (
    "current_objective",
    "likely_relevant_files",
    "likely_relevant_symbols",
    "changed_files",
    "verified_tests",
    "known_failures",
    "active_constraints",
    "next_action",
)


def persist_session_capsule(root: Path, facts: dict) -> Path:
    session_dir = state_dir(root) / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)
    compact = {key: facts[key] for key in SESSION_FIELDS if facts.get(key)}
    path = session_dir / "latest.json"
    path.write_text(json.dumps(compact, indent=2) + "\n", encoding="utf-8")
    return path


def build_session_capsule(root: Path, token_limit: int = 400) -> str:
    path = state_dir(root) / "sessions" / "latest.json"
    if not path.exists():
        return ""
    try:
        facts = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    parts = []
    for key in SESSION_FIELDS:
        value = facts.get(key)
        if not value:
            continue
        rendered = ", ".join(str(item) for item in value) if isinstance(value, list) else str(value)
        parts.append(f"{key}={rendered}")
    text = "ContextGuard resume capsule: " + "; ".join(parts)
    while estimate_tokens(text) > token_limit and parts:
        parts.pop()
        text = "ContextGuard resume capsule: " + "; ".join(parts)
    return text if parts else ""
