#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shlex
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from benchmarks.real_codex_backend_ab import (
    INITIAL_FILES,
    REFERENCE_FILES,
    _concurrency_probe,
    _json_command,
    _write,
    percent_change,
    prepare_codex_home,
    prepare_optimized_project,
    repository_hash,
    run_trial as backend_run_trial,
)


PROMPT = """Please investigate and fix the customer issue in SUPPORT_TICKET.md.

Treat this like a normal maintenance task in an unfamiliar repository:
- before editing, run `python3 -m pytest -q` exactly once and follow repository instructions for safe command execution
- reproduce the reported behavior from the ticket and available logs
- identify the root cause instead of applying a narrow data-specific workaround
- preserve existing public behavior unless the ticket shows it is broken
- add focused regression coverage for the bug
- run the complete public test suite and any useful targeted checks
- briefly document the fix in CHANGELOG.md

Do not weaken, delete, or skip tests. Work directly in the repository and finish when the issue is fixed and validation passes.
"""

RUN_ORDERS = [("raw", "contextguard"), ("contextguard", "raw"), ("raw", "contextguard")]

TICKET = """# Support ticket INC-4821

**Customer:** Northstar Retail
**Severity:** High

Since last week's rollout, customers occasionally receive a successful reservation response but later see stock below zero. Retrying the same checkout request sometimes reserves the item twice. A few older warehouse records also show zero available stock after startup even though the old export contains a positive quantity.

Operations attached excerpts from production logs. The issue is easiest to observe under parallel checkout traffic. Please reproduce it, fix the underlying problem without breaking existing API clients, add regression coverage, and add a short changelog note.
"""

PUBLIC_TESTS = r'''from inventory.api import handle_request
from inventory.migration import migrate_record
from inventory.service import InventoryService


def test_legacy_api_shape_remains_available():
    service = InventoryService([{"sku": "widget", "quantity": 10}])
    result = handle_request({"sku": "widget", "quantity": 2, "request_id": "public-1"}, service)
    assert {"sku", "quantity", "remaining", "ok"} <= result.keys()


def test_migration_keeps_sku():
    assert migrate_record({"sku": "widget", "quantity": 10})["sku"] == "widget"


def test_basic_reservation_reports_success():
    service = InventoryService([{"sku": "widget", "quantity": 10}])
    assert service.reserve("widget", 2, "public-2")["ok"] is True
'''

HIDDEN_TESTS = r'''from concurrent.futures import ThreadPoolExecutor

import pytest

from inventory.migration import migrate_record
from inventory.service import InventoryService


@pytest.mark.parametrize("quantity", range(1, 65))
def test_hidden_migration_preserves_legacy_quantity(quantity):
    result = migrate_record({"sku": f"sku-{quantity}", "quantity": quantity})
    assert result["available"] == quantity


@pytest.mark.parametrize("quantity", range(1, 49))
def test_hidden_retry_is_idempotent(quantity):
    service = InventoryService([{"sku": "widget", "quantity": quantity + 5}])
    first = service.reserve("widget", quantity, f"retry-{quantity}")
    second = service.reserve("widget", quantity, f"retry-{quantity}")
    assert first == second
    assert service.records["widget"]["available"] == 5


@pytest.mark.parametrize("stock", range(1, 33))
def test_hidden_parallel_checkout_never_oversells(stock):
    service = InventoryService([{"sku": "widget", "quantity": stock}])
    with ThreadPoolExecutor(max_workers=32) as pool:
        results = list(pool.map(lambda i: service.reserve("widget", 1, f"parallel-{i}"), range(stock * 2)))
    assert sum(item["ok"] for item in results) == stock
    assert service.records["widget"]["available"] == 0
    assert service.records["widget"]["reserved"] == stock
'''


def create_fixture(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    files = dict(INITIAL_FILES)
    files.pop("SPEC.md", None)
    files["SUPPORT_TICKET.md"] = TICKET
    files["CHANGELOG.md"] = "# Changelog\n\n## Unreleased\n\n"
    for relative, content in files.items():
        _write(root / relative, content)
    _write(root / "tests/test_public_behavior.py", PUBLIC_TESTS)
    _write(root / "data/production.log", "\n".join(
        f"ERROR checkout request=req-{i % 211} sku=sku-{i % 37} available={4 - (i % 9)} worker={i % 16}"
        for i in range(30000)
    ))
    _write(root / "data/warehouse-export.jsonl", "\n".join(
        json.dumps({"sku": f"sku-{i}", "quantity": i % 80 + 1, "schema_version": 1})
        for i in range(12000)
    ))
    _write(root / ".gitignore", ".contextguard/\n__pycache__/\n.pytest_cache/\n")
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "benchmark@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "ContextGuard Benchmark"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "legacy inventory service before incident fix"], cwd=root, check=True)
    return root


def apply_reference_solution(root: Path) -> None:
    for relative, content in REFERENCE_FILES.items():
        _write(root / relative, content)
    _write(root / "CHANGELOG.md", "# Changelog\n\n## Unreleased\n\n- Prevent duplicate and concurrent inventory reservations from overselling stock.\n")


def validate_fixture(root: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="contextguard-hidden-tests-") as tmp:
        hidden = Path(tmp) / "test_hidden_acceptance.py"
        hidden.write_text(HIDDEN_TESTS, encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "tests", str(hidden)],
            cwd=root, text=True, capture_output=True,
        )
    output = proc.stdout + proc.stderr
    passed = __import__("re").search(r"(\d+) passed", output)
    failed = __import__("re").search(r"(\d+) failed", output)
    canonical_exit, canonical = _json_command(root, "reserve", "scenario.json")
    hidden_total = 144
    total_passed = int(passed.group(1)) if passed else 0
    return {
        "exit_code": proc.returncode,
        "passed_tests": total_passed,
        "failed_tests": int(failed.group(1)) if failed else (0 if proc.returncode == 0 else 1),
        "hidden_passed_tests": hidden_total if proc.returncode == 0 else min(hidden_total, total_passed),
        "hidden_failed_tests": 0 if proc.returncode == 0 else max(1, hidden_total - min(hidden_total, total_passed)),
        "collected_tests": hidden_total + 3,
        "output": output,
        "canonical_exit_code": canonical_exit,
        "canonical_output": canonical,
        "concurrency_output": _concurrency_probe(root),
        "changelog_updated": len((root / "CHANGELOG.md").read_text().splitlines()) > 4,
    }


def build_codex_command(project: Path, *, optimized: bool) -> list[str]:
    command = shlex.split(os.environ.get("CONTEXTGUARD_CODEX_COMMAND", "codex"))
    command.extend([
        "exec", "--json", "--ephemeral", "--ignore-rules",
        "--model", "gpt-5.5", "-c", 'model_reasoning_effort="medium"',
        "--sandbox", "danger-full-access", "-c", 'approval_policy="never"',
        "-c", "features.plugins=false", "-C", str(project), PROMPT,
    ])
    return command


def run_trial(project: Path, home: Path, artifact_dir: Path, *, optimized: bool, timeout: int) -> dict:
    import benchmarks.real_codex_backend_ab as backend

    original_prompt = backend.PROMPT
    original_validate = backend.validate_fixture
    original_command = backend.build_codex_command
    try:
        backend.PROMPT = PROMPT
        backend.validate_fixture = validate_fixture
        backend.build_codex_command = build_codex_command
        return backend_run_trial(project, home, artifact_dir, optimized=optimized, timeout=timeout)
    finally:
        backend.PROMPT = original_prompt
        backend.validate_fixture = original_validate
        backend.build_codex_command = original_command


def _run_one(kind: str, root: Path, artifact_dir: Path, timeout: int) -> dict:
    project = create_fixture(root / f"{kind}-project")
    return run_trial(
        project,
        root / f"{kind}-home",
        artifact_dir,
        optimized=kind == "contextguard",
        timeout=timeout,
    )


def execute_three_run_ab(output_dir: Path, *, timeout: int = 1800) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    pairs = []
    for index, order in enumerate(RUN_ORDERS, start=1):
        results = {}
        for kind in order:
            with tempfile.TemporaryDirectory(prefix=f"contextguard-support-ab-{index}-{kind}-") as tmp:
                results[kind] = _run_one(kind, Path(tmp), output_dir / f"pair-{index}" / kind, timeout)
        raw_core = {key: results["raw"]["validation"]["canonical_output"].get(key) for key in ("sku", "quantity", "remaining", "ok")}
        contextguard_core = {key: results["contextguard"]["validation"]["canonical_output"].get(key) for key in ("sku", "quantity", "remaining", "ok")}
        accepted = all([
                results["raw"]["validation"]["exit_code"] == 0,
                results["contextguard"]["validation"]["exit_code"] == 0,
                raw_core == contextguard_core == {"sku": "widget", "quantity": 3, "remaining": 7, "ok": True},
                results["raw"]["validation"]["concurrency_output"] == results["contextguard"]["validation"]["concurrency_output"],
                results["raw"]["validation"]["changelog_updated"],
                results["contextguard"]["validation"]["changelog_updated"],
                results["raw"]["exact_baseline_command"],
                results["contextguard"]["capture_runner_used"],
        ])
        pairs.append({"pair": index, "order": list(order), "accepted": accepted, **results})
    keys = ["input_tokens", "cached_input_tokens", "uncached_input_tokens", "output_tokens", "reasoning_output_tokens", "tool_output_bytes", "elapsed_seconds", "command_executions"]
    aggregate = {}
    for key in keys:
        raw_values = [pair["raw"][key] for pair in pairs]
        cg_values = [pair["contextguard"][key] for pair in pairs]
        raw_median = statistics.median(raw_values)
        cg_median = statistics.median(cg_values)
        aggregate[key] = {
            "raw_values": raw_values,
            "contextguard_values": cg_values,
            "raw_median": raw_median,
            "contextguard_median": cg_median,
            "median_change_percent": percent_change(raw_median, cg_median),
        }
    result = {
        "benchmark": "real-codex-human-support-ticket-three-pair-ab",
        "model": "gpt-5.5", "reasoning_effort": "medium",
        "run_orders": [list(order) for order in RUN_ORDERS],
        "all_pairs_accepted": all(pair["accepted"] for pair in pairs),
        "pairs": pairs, "aggregate": aggregate,
        "limitations": [
            "Three controlled pairs reduce but do not eliminate model stochasticity.",
            "Hidden tests improve quality independence but cannot represent every production repository.",
            "Codex subscription quota accounting is not exposed by the CLI.",
        ],
    }
    (output_dir / "summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=PLUGIN_ROOT / "benchmarks/results/real-codex-support-ab-2026-06-13")
    parser.add_argument("--timeout", type=int, default=1800)
    args = parser.parse_args(argv)
    if args.self_check:
        with tempfile.TemporaryDirectory(prefix="contextguard-support-check-") as tmp:
            project = create_fixture(Path(tmp) / "fixture")
            before = validate_fixture(project)
            apply_reference_solution(project)
            after = validate_fixture(project)
            print(json.dumps({"before": before["exit_code"], "after": after["exit_code"], "hidden_passed": after["hidden_passed_tests"], "canonical": after["canonical_output"]}, sort_keys=True))
            return int(after["exit_code"] != 0)
    if args.run:
        result = execute_three_run_ab(args.output_dir, timeout=args.timeout)
        print(json.dumps(result["aggregate"], indent=2, sort_keys=True))
        return int(not result["all_pairs_accepted"])
    parser.error("choose --self-check or --run")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
