#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from benchmarks import real_codex_ci_ab as ci


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
ROUTING_DIRECTIVE = """

ContextGuard model routing decision: this task has a bounded, low-risk implementation package. After initial
orientation and root-cause analysis, you must start exactly one contextguard-worker for implementation and
focused tests. Start it with an isolated prompt and explicit file ownership, not a full-history fork. The parent
must retain design and risk decisions, review the worker diff, and run final validation. If the worker is
unavailable or incomplete, continue locally and report the fallback.
"""

PRICES_PER_MILLION = {
    "gpt-5.5": {"input": 5.0, "cached_input": 0.5, "output": 30.0},
    "gpt-5.4-mini": {"input": 0.75, "cached_input": 0.075, "output": 4.5},
}


def estimate_api_cost(result: dict, model: str) -> float:
    prices = PRICES_PER_MILLION[model]
    cached = result["cached_input_tokens"]
    uncached = result["input_tokens"] - cached
    return round((
        uncached * prices["input"]
        + cached * prices["cached_input"]
        + result["output_tokens"] * prices["output"]
    ) / 1_000_000, 6)


def routing_evidence(artifact_dir: Path, project: Path) -> dict:
    events = []
    for line in (artifact_dir / "events.jsonl").read_text(encoding="utf-8").splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    spawns = [
        event for event in events
        if (event.get("item") or {}).get("type") == "collab_tool_call"
        and (event.get("item") or {}).get("tool") == "spawn_agent"
        and (event.get("item") or {}).get("status") == "completed"
        and (event.get("item") or {}).get("receiver_thread_ids")
    ]
    state_path = project / ".contextguard" / "sessions" / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    agent_path = project / ".codex" / "agents" / "contextguard-worker.toml"
    agent = agent_path.read_text(encoding="utf-8") if agent_path.exists() else ""
    stderr = (artifact_dir / "stderr.txt").read_text(encoding="utf-8")
    return {
        "successful_spawn_count": len(spawns),
        "worker_start_events": [e for e in state.get("routing_events", []) if e.get("event") == "start"],
        "worker_agent_configured": 'name = "contextguard-worker"' in agent and 'model = "gpt-5.4-mini"' in agent,
        "full_history_model_error": "Full-history forked agents inherit" in stderr,
    }


def run_kind(kind: str, root: Path, artifact_dir: Path, timeout: int) -> dict:
    project = ci.create_fixture(root / "project")
    original_prompt = ci.PROMPT
    try:
        ci.PROMPT = original_prompt + (ROUTING_DIRECTIVE if kind == "routed" else "")
        result = ci.run_trial(
            project, root / "home", artifact_dir,
            optimized=kind == "routed", timeout=timeout, model="gpt-5.5",
        )
    finally:
        ci.PROMPT = original_prompt
    result["routing"] = routing_evidence(artifact_dir, project) if kind == "routed" else {}
    return result


def execute_ab(output_dir: Path, *, timeout: int = 1800) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    for kind in ("raw", "routed"):
        with tempfile.TemporaryDirectory(prefix=f"contextguard-model-routing-{kind}-") as tmp:
            results[kind] = run_kind(kind, Path(tmp), output_dir / kind, timeout)

    raw, routed = results["raw"], results["routed"]
    same_quality = all([
        raw["validation"]["exit_code"] == 0,
        routed["validation"]["exit_code"] == 0,
        raw["validation"]["hidden_passed_tests"] == routed["validation"]["hidden_passed_tests"] == 160,
        raw["validation"]["canonical_output"] == routed["validation"]["canonical_output"],
        raw["validation"]["changelog_updated"],
        routed["validation"]["changelog_updated"],
    ])
    routing = routed["routing"]
    route_proven = all([
        routing["successful_spawn_count"] == 1,
        routing["worker_agent_configured"],
        not routing["full_history_model_error"],
    ])
    summary = {
        "benchmark": "real-codex-gpt-5.5-parent-gpt-5.4-mini-worker-ab",
        "same_quality": same_quality,
        "routing_proven": route_proven,
        "accepted": same_quality and route_proven,
        "raw": raw,
        "routed": routed,
        "api_cost_usd": {
            "raw_gpt_5_5": estimate_api_cost(raw, "gpt-5.5"),
            "routed_lower_bound_if_all_tokens_were_mini": estimate_api_cost(routed, "gpt-5.4-mini"),
            "routed_upper_bound_if_all_tokens_were_parent": estimate_api_cost(routed, "gpt-5.5"),
            "note": "Codex CLI reports aggregate parent and child usage, not per-agent token allocation.",
        },
        "limitations": [
            "One controlled pair proves execution and quality but does not eliminate model stochasticity.",
            "Codex CLI does not expose exact per-agent billing or subscription usage-limit accounting.",
            "The routed prompt reproduces the additional context injected by ContextGuard's UserPromptSubmit hook.",
        ],
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    parser.add_argument(
        "--output-dir", type=Path,
        default=PLUGIN_ROOT / "benchmarks" / "results" / "real-codex-model-routing-ab-2026-06-14",
    )
    parser.add_argument("--timeout", type=int, default=1800)
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("choose --run")
    result = execute_ab(args.output_dir, timeout=args.timeout)
    print(json.dumps({
        "accepted": result["accepted"],
        "same_quality": result["same_quality"],
        "routing_proven": result["routing_proven"],
        "api_cost_usd": result["api_cost_usd"],
    }, indent=2, sort_keys=True))
    return int(not result["accepted"])


if __name__ == "__main__":
    raise SystemExit(main())
