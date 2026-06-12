#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SOURCE_PLUGIN = Path(__file__).resolve().parents[1]
if str(SOURCE_PLUGIN) not in sys.path:
    sys.path.insert(0, str(SOURCE_PLUGIN))

from benchmarks.real_codex_ab import parse_codex_jsonl

PROMPT = (
    "Run `python3 emit_failures.py` exactly once. Follow the repository instructions for safe "
    "command execution. The command intentionally fails; do not retry or inspect files. "
    "After observing the result, reply exactly: OBSERVED 130 FAILURES"
)


def create_fixture(root: Path) -> Path:
    root.mkdir(parents=True)
    (root / "emit_failures.py").write_text(
        "for index in range(130):\n"
        "    print(f'FAILED tests/test_host.py::test_case_{index} - AssertionError: deterministic failure {index}')\n"
        "    for frame in range(4):\n"
        "        print(f'  File src/service.py, line {100 + frame}, in case_{index}: frame={frame}')\n"
        "print('130 failed in 0.50s')\n"
        "raise SystemExit(1)\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "benchmark@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "ContextGuard Benchmark"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "initial fixture"], cwd=root, check=True)
    return root


def _plugin_environment(plugin: Path) -> dict[str, str]:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(plugin)
    return environment


def initialize(plugin: Path, project: Path) -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "contextguard.cli", "init", "--path", str(project)],
        cwd=plugin,
        env=_plugin_environment(plugin),
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout + proc.stderr)


def deterministic_self_check(project: Path, plugin: Path) -> dict:
    command = [sys.executable, str(project / "emit_failures.py")]
    raw = subprocess.run(command, cwd=project, text=True, capture_output=True)
    raw_output = raw.stdout + raw.stderr
    initialize(plugin, project)
    runner = project / ".contextguard" / "bin" / "contextguard"
    protected = subprocess.run(
        [str(runner), "capture", "--", *command],
        cwd=project,
        text=True,
        capture_output=True,
    )
    summary_path = sorted((project / ".contextguard" / "tmp").glob("command-*.summary.json"))[-1]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    archived = Path(summary["stdout_path"]).read_text(encoding="utf-8") + Path(
        summary["stderr_path"]
    ).read_text(encoding="utf-8")
    visible = protected.stdout + protected.stderr
    return {
        "same_exit_code": raw.returncode == protected.returncode,
        "archived_raw_matches": hashlib.sha256(raw_output.encode()).hexdigest()
        == hashlib.sha256(archived.encode()).hexdigest(),
        "runner_used": "ContextGuard capture summary" in visible,
        "raw_bytes": len(raw_output.encode()),
        "visible_bytes": len(visible.encode()),
        "visible_output_reduced": len(visible.encode()) < len(raw_output.encode()),
    }


def _prepare_home(home: Path, project: Path) -> None:
    home.mkdir(parents=True)
    auth = Path.home() / ".codex" / "auth.json"
    if not auth.exists():
        raise RuntimeError("Codex authentication is unavailable at ~/.codex/auth.json")
    shutil.copy2(auth, home / "auth.json")
    os.chmod(home / "auth.json", 0o600)
    canonical = Path(os.path.realpath(project)).as_posix()
    (home / "config.toml").write_text(
        f'[projects."{canonical}"]\ntrust_level = "trusted"\n', encoding="utf-8"
    )


def _run_codex(project: Path, home: Path, artifact: Path, timeout: int) -> dict:
    _prepare_home(home, project)
    command = shlex.split(os.environ.get("CONTEXTGUARD_CODEX_COMMAND", "codex"))
    command.extend([
        "exec", "--json", "--ephemeral", "--ignore-rules", "--model", "gpt-5.5",
        "-c", 'model_reasoning_effort="low"', "--sandbox", "danger-full-access",
        "-c", 'approval_policy="never"', "-c", "features.plugins=false",
        "-C", str(project), PROMPT,
    ])
    environment = os.environ.copy()
    environment["CODEX_HOME"] = str(home)
    started = time.perf_counter()
    proc = subprocess.run(command, cwd=project, env=environment, text=True, capture_output=True, timeout=timeout)
    elapsed = time.perf_counter() - started
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(proc.stdout, encoding="utf-8")
    parsed = parse_codex_jsonl(proc.stdout)
    parsed.update({
        "codex_exit_code": proc.returncode,
        "elapsed_seconds": round(elapsed, 3),
        "raw_command_used": any(
            "python3 emit_failures.py" in item and ".contextguard/bin/contextguard" not in item
            for item in parsed["commands"]
        ),
        "capture_runner_used": any(
            ".contextguard/bin/contextguard" in item and "capture" in item
            and "python3 emit_failures.py" in item for item in parsed["commands"]
        ),
    })
    return parsed


def _percent_change(raw: int | float, protected: int | float) -> float | None:
    if not raw:
        return None
    return round((protected - raw) / raw * 100, 2)


def run_real_ab(output_dir: Path, plugin: Path, timeout: int) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="contextguard-host-capture-ab-") as tmp:
        root = Path(tmp)
        raw_project = create_fixture(root / "raw")
        protected_project = create_fixture(root / "protected")
        initialize(plugin, protected_project)
        raw = _run_codex(raw_project, root / "raw-home", output_dir / "raw.jsonl", timeout)
        protected = _run_codex(protected_project, root / "protected-home", output_dir / "protected.jsonl", timeout)
        equivalent = (
            raw["codex_exit_code"] == 0 and protected["codex_exit_code"] == 0
            and raw["final_response"].strip() == "OBSERVED 130 FAILURES"
            and protected["final_response"].strip() == raw["final_response"].strip()
            and raw["raw_command_used"] and protected["capture_runner_used"]
            and raw["command_executions"] == 1 and protected["command_executions"] == 1
        )
        comparison = {
            key: {
                "raw": raw[key], "contextguard": protected[key],
                "change_percent": _percent_change(raw[key], protected[key]),
            }
            for key in (
                "input_tokens", "cached_input_tokens", "uncached_input_tokens",
                "output_tokens", "tool_output_bytes", "elapsed_seconds",
            )
        }
        result = {
            "benchmark": "real-codex-host-independent-capture-ab",
            "same_prompt": True, "model": "gpt-5.5", "reasoning_effort": "low",
            "plugin_root": plugin.name, "equivalent_result": equivalent,
            "raw": raw, "contextguard": protected, "comparison": comparison,
            "limitations": ["Single controlled sample; model execution is stochastic."],
        }
        (output_dir / "summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--plugin-root", type=Path, default=SOURCE_PLUGIN)
    parser.add_argument("--output-dir", type=Path, default=SOURCE_PLUGIN / "benchmarks" / "results" / "host-capture-ab-2026-06-12")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args(argv)
    if args.self_check:
        with tempfile.TemporaryDirectory(prefix="contextguard-host-self-check-") as tmp:
            result = deterministic_self_check(create_fixture(Path(tmp) / "fixture"), args.plugin_root)
        print(json.dumps(result, indent=2, sort_keys=True))
        required = ("same_exit_code", "archived_raw_matches", "runner_used", "visible_output_reduced")
        return int(not all(result[key] for key in required))
    if args.run:
        result = run_real_ab(args.output_dir, args.plugin_root, args.timeout)
        print(json.dumps(result["comparison"], indent=2, sort_keys=True))
        return int(not result["equivalent_result"])
    parser.error("choose --self-check or --run")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
