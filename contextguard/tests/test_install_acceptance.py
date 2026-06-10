import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_install_acceptance_covers_empty_existing_and_automatic_hooks(tmp_path):
    output = tmp_path / "acceptance.json"
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "benchmarks/install_acceptance.py"),
            "--output",
            str(output),
            "--timing-samples",
            "1",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    result = json.loads(output.read_text())
    assert result["accepted"] is True
    assert result["empty_project"]["initialized"] is True
    assert result["empty_project"]["project_kind"] == "empty"
    assert result["existing_project"]["initialized"] is True
    assert result["existing_project"]["project_kind"] == "existing"
    assert result["existing_project"]["user_content_preserved"] is True
    assert result["automatic_hooks"]["session_start"] is True
    assert result["automatic_hooks"]["user_prompt_submit"] is True
    assert result["automatic_hooks"]["pre_tool_use"] is True
    assert result["automatic_hooks"]["post_tool_use"] is True
    assert result["output_equivalence"]["archived_raw_matches"] is True
    assert result["output_equivalence"]["summary_and_failed_tests_preserved"] is True
    assert result["tokens"]["saved"] > 0
    assert result["tokens"]["reduction_percent"] > 0
