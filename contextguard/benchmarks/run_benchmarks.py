#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
import os
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]


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
    project.mkdir()
    if name == "verbose-test-output":
        script = project / "test_output.py"
        script.write_text("for i in range(500): print(f'ERROR failure {i}')\nraise SystemExit(1)\n")
        return project, [sys.executable, str(script)]
    if name == "large-json":
        data = [{"id": i, "status": "error" if i % 10 == 0 else "ok"} for i in range(1000)]
        path = project / "data.json"
        path.write_text(json.dumps(data))
        return project, ["cat", str(path)]
    if name == "small-web-project":
        (project / "package.json").write_text('{"scripts":{"test":"echo ok","dev":"vite"}}\n')
        (project / "src").mkdir()
        (project / "src" / "main.ts").write_text("export function start() { return 'ok' }\n")
        return project, ["find", "."]
    if name == "repeated-log-errors":
        path = project / "app.log"
        path.write_text("\n".join(f"ERROR repeated failure {i}" for i in range(500)))
        return project, ["cat", str(path)]
    (project / "app.py").write_text("def main():\n    return 'ok'\n")
    return project, ["find", "."]


def main() -> int:
    fixture_names = [
        "small-web-project",
        "medium-node-project",
        "python-data-project",
        "verbose-test-output",
        "large-json",
        "repeated-log-errors",
        "existing-undocumented-repository",
    ]
    with tempfile.TemporaryDirectory(prefix="contextguard-bench-") as tmp:
        tmp_path = Path(tmp)
        results = []
        for name in fixture_names:
            project, command = create_fixture(tmp_path, name)
            raw_code, raw_bytes, raw_seconds = run(command, project)
            guard_code, guard_bytes, guard_seconds = contextguard(command, project)
            results.append(
                {
                    "fixture": name,
                    "raw_exit": raw_code,
                    "contextguard_exit": guard_code,
                    "raw_bytes": raw_bytes,
                    "contextguard_bytes": guard_bytes,
                    "contextguard_overhead_bytes": max(0, guard_bytes - raw_bytes),
                    "raw_seconds": round(raw_seconds, 4),
                    "contextguard_seconds": round(guard_seconds, 4),
                    "information_retained": "exit code, byte counts, error signatures and full local output path",
                }
            )
        print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
