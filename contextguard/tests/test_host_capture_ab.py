import subprocess
import sys
from pathlib import Path

from benchmarks.host_capture_ab import PROMPT, create_fixture, deterministic_self_check


ROOT = Path(__file__).resolve().parents[1]


def test_host_capture_prompt_is_identical_and_requires_repository_instructions():
    assert "python3 emit_failures.py" in PROMPT
    assert "Follow the repository instructions" in PROMPT
    assert "OBSERVED 130 FAILURES" in PROMPT


def test_host_capture_fixture_and_local_runner_are_equivalent(tmp_path: Path):
    project = create_fixture(tmp_path / "fixture")
    result = deterministic_self_check(project, ROOT)

    assert result["same_exit_code"] is True
    assert result["archived_raw_matches"] is True
    assert result["runner_used"] is True
    assert result["visible_output_reduced"] is True


def test_host_capture_benchmark_self_check_runs_standalone(tmp_path: Path):
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "benchmarks" / "host_capture_ab.py"),
            "--self-check",
            "--output-dir",
            str(tmp_path / "result"),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
