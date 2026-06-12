import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_hook(name: str, payload: dict, cwd: Path):
    proc = subprocess.run(
        [sys.executable, str(ROOT / "hooks" / name)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        cwd=cwd,
        check=True,
    )
    return json.loads(proc.stdout)


def test_hook_json_input_output(tmp_path: Path):
    result = run_hook("pre_tool_use.py", {"tool_name": "Bash", "tool_input": {"command": "cat big.log"}}, tmp_path)
    output = result["hookSpecificOutput"]
    assert output["hookEventName"] == "PreToolUse"
    assert output["permissionDecision"] == "allow"
    assert "/scripts/contextguard" in output["updatedInput"]["command"]


def test_python_module_pytest_pipeline_is_rewritten(tmp_path: Path):
    result = run_hook(
        "pre_tool_use.py",
        {"tool_name": "Bash", "tool_input": {"command": "python3 -m pytest -q 2>&1 | tee /tmp/tests.log"}},
        tmp_path,
    )
    command = result["hookSpecificOutput"]["updatedInput"]["command"]
    assert "/scripts/contextguard" in command
    assert "python3 -m pytest" in command


def test_stop_hook_loop_prevention(tmp_path: Path):
    result = run_hook("stop.py", {"stop_hook_active": True}, tmp_path)
    assert result == {}


def test_session_start_automatically_initializes_empty_project(tmp_path: Path):
    result = run_hook("session_start.py", {}, tmp_path)

    assert "initialized automatically" in result["hookSpecificOutput"]["additionalContext"]
    assert (tmp_path / ".contextguard" / "manifest.json").exists()
    assert (tmp_path / ".contextguard" / "tmp" / "hook-heartbeats.jsonl").exists()


def test_session_start_preserves_existing_project_content(tmp_path: Path):
    agents = tmp_path / "AGENTS.md"
    agents.write_text("# User instructions\n\nNever remove this.\n")
    (tmp_path / "app.py").write_text("print('ok')\n")

    run_hook("session_start.py", {}, tmp_path)

    assert "Never remove this." in agents.read_text()
    assert "BEGIN CONTEXTGUARD MANAGED SECTION" in agents.read_text()


def test_session_start_initialized_is_silent(tmp_path: Path):
    state = tmp_path / ".contextguard"
    state.mkdir()
    (state / "manifest.json").write_text("{}")
    result = run_hook("session_start.py", {}, tmp_path)
    assert result == {}


def test_status_reports_session_hook_as_partial_until_tool_hook_runs(tmp_path: Path):
    run_hook("session_start.py", {}, tmp_path)
    proc = subprocess.run(
        [sys.executable, "-m", "contextguard.cli", "status"],
        cwd=tmp_path,
        env={"PYTHONPATH": str(ROOT)},
        text=True,
        capture_output=True,
        check=True,
    )

    assert "Hook status: partially observed" in proc.stdout
    assert "SessionStart" in proc.stdout

    run_hook("pre_tool_use.py", {"tool_name": "Bash", "tool_input": {"command": "pytest -q"}}, tmp_path)
    verified = subprocess.run(
        [sys.executable, "-m", "contextguard.cli", "status"],
        cwd=tmp_path,
        env={"PYTHONPATH": str(ROOT)},
        text=True,
        capture_output=True,
        check=True,
    )
    assert "Hook status: observed" in verified.stdout
    assert "PreToolUse" in verified.stdout


def test_post_tool_use_stores_large_output(tmp_path: Path):
    payload = {"tool_name": "Bash", "tool_response": "ERROR repeated failure\n" * 5000}
    result = run_hook("post_tool_use.py", payload, tmp_path)
    assert result["decision"] == "block"
    assert "full_output:" in result["reason"]
    assert result["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
    assert list((tmp_path / ".contextguard" / "tmp").glob("tool-output-*.txt"))
    metrics = tmp_path / ".contextguard" / "tmp" / "hook-output-metrics.jsonl"
    record = json.loads(metrics.read_text().splitlines()[-1])
    assert record["raw_bytes"] > record["model_visible_bytes"]


def test_post_tool_use_compacts_noisy_medium_output(tmp_path: Path):
    payload = {"tool_name": "Bash", "tool_response": "FAILED test_case file.py:12 error\n" * 80}
    result = run_hook("post_tool_use.py", payload, tmp_path)
    assert result["decision"] == "block"
    assert len(result["reason"].encode()) < 2000


def test_post_tool_use_keeps_failed_test_names_visible(tmp_path: Path):
    output = "\n".join(
        ["FAILED tests/test_orders.py::test_cap - AssertionError: cap"]
        + [f"FAILED tests/test_orders.py::test_case_{index} - AssertionError" for index in range(40)]
        + ["41 failed in 0.25s"]
    )
    result = run_hook("post_tool_use.py", {"tool_name": "Bash", "tool_response": output}, tmp_path)
    assert "failed_tests:" in result["reason"]
    assert "tests/test_orders.py::test_cap" in result["reason"]
    assert "41 failed in 0.25s" in result["reason"]


def test_pre_compact_persists_compact_session_facts(tmp_path: Path):
    result = run_hook(
        "pre_compact.py",
        {"current_objective": "finish policy", "changed_files": ["a.py"], "transcript": "x" * 10000},
        tmp_path,
    )
    assert result == {}
    capsule = (tmp_path / ".contextguard" / "sessions" / "latest.json").read_text()
    assert "finish policy" in capsule
    assert "transcript" not in capsule


def test_user_prompt_context_uses_codex_hook_envelope(tmp_path: Path):
    state = tmp_path / ".contextguard"
    state.mkdir()
    (state / "manifest.json").write_text("{}")
    result = run_hook("user_prompt_submit.py", {"prompt": "fix billing"}, tmp_path)
    output = result["hookSpecificOutput"]
    assert output["hookEventName"] == "UserPromptSubmit"
    assert "ContextGuard" in output["additionalContext"]
