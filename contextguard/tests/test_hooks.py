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
    assert result["permissionDecision"] == "allow"
    assert "updatedInput" in result
    assert "/scripts/contextguard" in result["updatedInput"]["command"]


def test_stop_hook_loop_prevention(tmp_path: Path):
    result = run_hook("stop.py", {"stop_hook_active": True}, tmp_path)
    assert result == {}


def test_session_start_uninitialized(tmp_path: Path):
    result = run_hook("session_start.py", {}, tmp_path)
    assert "not initialized" in result["additionalContext"]


def test_session_start_initialized_is_silent(tmp_path: Path):
    state = tmp_path / ".contextguard"
    state.mkdir()
    (state / "manifest.json").write_text("{}")
    result = run_hook("session_start.py", {}, tmp_path)
    assert result == {}


def test_post_tool_use_stores_large_output(tmp_path: Path):
    payload = {"output": "ERROR repeated failure\n" * 5000}
    result = run_hook("post_tool_use.py", payload, tmp_path)
    assert "replacementOutput" in result
    assert "full_output:" in result["replacementOutput"]
    assert list((tmp_path / ".contextguard" / "tmp").glob("tool-output-*.txt"))


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
