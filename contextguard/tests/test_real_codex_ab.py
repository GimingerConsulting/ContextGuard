import json
import subprocess
import sys
from pathlib import Path

from benchmarks.real_codex_ab import (
    PROMPT,
    apply_reference_solution,
    build_codex_command,
    create_fixture,
    parse_codex_jsonl,
    prepare_optimized_project,
    validate_fixture,
)


def test_prompt_forces_same_noisy_baseline_before_edits():
    assert "before editing" in PROMPT
    assert "python3 -m pytest -q" in PROMPT
    assert "follow the repository instructions" in PROMPT


def test_hard_fixture_fails_before_reference_and_passes_after(tmp_path: Path):
    project = create_fixture(tmp_path / "fixture")
    before = validate_fixture(project)
    assert before["exit_code"] != 0
    assert before["collected_tests"] >= 130

    apply_reference_solution(project)
    after = validate_fixture(project)
    assert after["exit_code"] == 0
    assert after["failed_tests"] == 0
    assert after["canonical_output"]["settlement_id"] == "stl-001"
    assert after["canonical_output"]["posted_minor"] == 9174


def test_parse_codex_jsonl_extracts_exact_usage_and_tool_output():
    events = [
        {"type": "item.completed", "item": {"type": "command_execution", "aggregated_output": "abc\ndef\n"}},
        {"type": "item.completed", "item": {"type": "file_change", "changes": [{"path": "a.py"}]}},
        {"type": "item.completed", "item": {"type": "agent_message", "text": "done"}},
        {
            "type": "turn.completed",
            "usage": {
                "input_tokens": 1000,
                "cached_input_tokens": 600,
                "output_tokens": 80,
                "reasoning_output_tokens": 20,
            },
        },
    ]
    parsed = parse_codex_jsonl("\n".join(json.dumps(event) for event in events))
    assert parsed["input_tokens"] == 1000
    assert parsed["uncached_input_tokens"] == 400
    assert parsed["output_tokens"] == 80
    assert parsed["reasoning_output_tokens"] == 20
    assert parsed["tool_output_bytes"] == 8
    assert parsed["command_executions"] == 1
    assert parsed["file_changes"] == 1
    assert parsed["final_response"] == "done"
    assert parsed["commands"] == [""]


def test_raw_and_optimized_commands_differ_only_by_hook_activation(tmp_path: Path):
    raw = build_codex_command(tmp_path / "raw", optimized=False)
    optimized = build_codex_command(tmp_path / "optimized", optimized=True)
    normalized = list(optimized)
    normalized[normalized.index(str(tmp_path / "optimized"))] = str(tmp_path / "raw")
    assert raw == normalized
    assert raw[-1] == optimized[-1]
    assert "gpt-5.5" in raw
    assert 'model_reasoning_effort="medium"' in raw


def test_real_ab_accepts_optimized_trial_only_when_project_runner_is_used():
    source = (Path(__file__).resolve().parents[1] / "benchmarks" / "real_codex_ab.py").read_text()

    assert 'capture_runner_used' in source
    assert '.contextguard/bin/contextguard' in source
    assert 'optimized["capture_runner_used"]' in source


def test_real_ab_no_longer_requires_codex_exec_hook_dispatch():
    source = (Path(__file__).resolve().parents[1] / "benchmarks" / "real_codex_ab.py").read_text()

    assert 'hook_invocations' not in source
    assert 'compacted_output_count' not in source
    assert 'optimized["capture_runner_used"]' in source


def test_optimized_command_does_not_depend_on_hook_trust_bypass(tmp_path: Path):
    raw = build_codex_command(tmp_path / "raw", optimized=False)
    optimized = build_codex_command(tmp_path / "optimized", optimized=True)
    assert "--dangerously-bypass-hook-trust" not in raw
    assert "--dangerously-bypass-hook-trust" not in optimized


def test_optimized_project_uses_initialized_host_independent_runner(tmp_path: Path):
    project = create_fixture(tmp_path / "optimized")
    prepare_optimized_project(project)
    assert (project / ".contextguard/manifest.json").exists()
    assert (project / ".contextguard/bin/contextguard").exists()
    assert not (project / ".codex/hooks.json").exists()
