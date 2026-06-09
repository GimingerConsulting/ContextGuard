from __future__ import annotations

from pathlib import Path

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
        files = "\n".join(f"- {path}" for path in result["likely_files"])
        text = (
            "ContextGuard task capsule\n"
            f"confidence: {result['confidence']}\n"
            "likely relevant files:\n"
            f"{files}\n"
            "recommended initial scope: metadata, search hits and focused ranges first."
        )
    while estimate_tokens(text) > token_limit and "\n-" in text:
        text = "\n".join(text.splitlines()[:-1])
    return text
