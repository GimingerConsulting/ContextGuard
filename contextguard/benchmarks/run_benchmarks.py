#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from contextguard.output_policy import inspect_final_response


def env() -> dict[str, str]:
    current = os.environ.copy()
    current["PYTHONPATH"] = f"{PLUGIN_ROOT}{os.pathsep}{current.get('PYTHONPATH', '')}".rstrip(os.pathsep)
    return current


def run(command: list[str], cwd: Path) -> tuple[int, int, float]:
    started = time.time()
    proc = subprocess.run(command, cwd=cwd, text=True, capture_output=True, env=env())
    return proc.returncode, len(proc.stdout.encode()) + len(proc.stderr.encode()), time.time() - started


def contextguard(command: list[str], cwd: Path) -> tuple[int, int, float]:
    return run([sys.executable, "-m", "contextguard.cli", "capture", "--", *command], cwd)


def create_fixture(root: Path, name: str) -> tuple[Path, list[str]]:
    project = root / name
    project.mkdir(parents=True)
    if name == "verbose-test-suite":
        script = project / "test_output.py"
        script.write_text("for i in range(500): print(f'FAILED test_case_{i} app.py:{i}: error')\nraise SystemExit(1)\n")
        return project, [sys.executable, str(script)]
    if name == "large-json-analysis":
        path = project / "data.json"
        path.write_text(json.dumps([{"id": i, "status": "error" if i % 10 == 0 else "ok"} for i in range(1000)]))
        return project, ["cat", str(path)]
    if name == "repeated-log-errors":
        path = project / "app.log"
        path.write_text("\n".join(f"ERROR repeated failure {i}" for i in range(500)))
        return project, ["cat", str(path)]
    if name == "trivial-one-file-change":
        path = project / "app.py"
        path.write_text("VALUE = 1\n")
        return project, [sys.executable, "-c", "from pathlib import Path; Path('app.py').write_text('VALUE = 2\\n')"]
    if name == "medium-feature":
        (project / "service.py").write_text("def enabled(): return False\n")
        return project, [sys.executable, "-c", "from pathlib import Path; Path('feature.py').write_text('def enabled(): return True\\n')"]
    if name == "complex-debugging":
        script = project / "debug.py"
        script.write_text("print('Traceback (most recent call last):')\nprint('ValueError: broken')\nraise SystemExit(1)\n")
        return project, [sys.executable, str(script)]
    if name == "session-restart-partial-changes":
        (project / "partial.py").write_text("STEP = 1\n")
    elif name == "large-existing-repository":
        for index in range(300):
            (project / f"module_{index}.py").write_text(f"VALUE = {index}\n")
    else:
        (project / "app.py").write_text("def main():\n    return 'ok'\n")
    return project, ["find", ".", "-type", "f"]


def repository_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".contextguard" in path.parts:
            continue
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> int:
    fixture_names = [
        "trivial-one-file-change",
        "medium-feature",
        "complex-debugging",
        "verbose-test-suite",
        "large-json-analysis",
        "repeated-log-errors",
        "long-multi-turn-session",
        "session-restart-unchanged",
        "session-restart-partial-changes",
        "large-existing-repository",
    ]
    with tempfile.TemporaryDirectory(prefix="contextguard-bench-") as tmp:
        tmp_path = Path(tmp)
        results = []
        for name in fixture_names:
            raw_project, raw_command = create_fixture(tmp_path / "baseline", name)
            guard_project, guard_command = create_fixture(tmp_path / "optimized", name)
            raw_code, raw_bytes, raw_seconds = run(raw_command, raw_project)
            guard_code, guard_bytes, guard_seconds = contextguard(guard_command, guard_project)
            raw_hash = repository_hash(raw_project)
            guard_hash = repository_hash(guard_project)
            saved = raw_bytes - guard_bytes
            results.append(
                {
                    "fixture": name,
                    "raw_exit": raw_code,
                    "contextguard_exit": guard_code,
                    "raw_bytes": raw_bytes,
                    "contextguard_bytes": guard_bytes,
                    "tool_output_bytes_avoided": max(0, saved),
                    "contextguard_overhead_bytes": max(0, -saved),
                    "net_estimated_reduction": saved // 4,
                    "raw_seconds": round(raw_seconds, 4),
                    "contextguard_seconds": round(guard_seconds, 4),
                    "result_hash": guard_hash,
                    "same_result": raw_code == guard_code and raw_hash == guard_hash,
                    "output_quality": inspect_final_response(
                        f"Changed {name}. Validation: equivalent exit code and repository hash.",
                        changed_files=[name],
                        validation_required=True,
                    )["valid"],
                    "measurement": "bytes and duration measured; token reduction estimated at four bytes per token",
                }
            )
        print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
