import json
import subprocess
import sys
from pathlib import Path

import pytest

from benchmarks.real_codex_ab import (
    apply_reference_solution,
    build_codex_command,
    create_fixture,
    parse_codex_jsonl,
    prepare_optimized_project,
    validate_fixture,
)


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


def test_raw_and_optimized_commands_differ_only_by_hook_activation(tmp_path: Path):
    raw = build_codex_command(tmp_path / "raw", optimized=False)
    optimized = build_codex_command(tmp_path / "optimized", optimized=True)
    normalized = list(optimized)
    normalized[normalized.index(str(tmp_path / "optimized"))] = str(tmp_path / "raw")
    assert raw == normalized
    assert raw[-1] == optimized[-1]
    assert "gpt-5.5" in raw
    assert 'model_reasoning_effort="medium"' in raw


def test_optimized_project_has_initialized_state_and_current_hook_schema(tmp_path: Path):
    project = create_fixture(tmp_path / "optimized")
    prepare_optimized_project(project)
    assert (project / ".contextguard/manifest.json").exists()
    hooks = json.loads((project / ".codex/hooks.json").read_text())
    assert hooks["hooks"]["PreToolUse"][0]["matcher"] == "Bash"
    assert hooks["hooks"]["PreToolUse"][0]["hooks"][0]["type"] == "command"
