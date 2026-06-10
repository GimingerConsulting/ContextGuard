import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_benchmark_harness_runs():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "benchmarks" / "run_benchmarks.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(proc.stdout)
    assert len(payload) >= 10
    assert all(item["raw_exit"] == item["contextguard_exit"] for item in payload)
    assert all(item["same_result"] for item in payload)
    assert all(item["output_quality"] for item in payload)
    assert all("result_hash" in item for item in payload)
    assert all("net_estimated_reduction" in item for item in payload)
