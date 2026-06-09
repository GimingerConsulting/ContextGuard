from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from .config import state_dir
from .database import connect, increment
from .output_compactor import compact_output


def capture(root: Path, argv: list[str]) -> int:
    tmp_dir = state_dir(root) / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    started = time.time()
    proc = subprocess.run(argv, cwd=root, text=True, capture_output=True)
    duration_ms = int((time.time() - started) * 1000)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = tmp_dir / f"command-{stamp}-{int(started * 1000)}"
    stdout_path = base.with_suffix(".stdout.txt")
    stderr_path = base.with_suffix(".stderr.txt")
    summary_path = base.with_suffix(".summary.json")
    stdout_path.write_text(proc.stdout, encoding="utf-8", errors="replace")
    stderr_path.write_text(proc.stderr, encoding="utf-8", errors="replace")
    summary = compact_output(proc.stdout, proc.stderr)
    summary.update(
        {
            "command": argv,
            "exit_code": proc.returncode,
            "duration_ms": duration_ms,
            "stdout_path": stdout_path.as_posix(),
            "stderr_path": stderr_path.as_posix(),
        }
    )
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    conn = connect(state_dir(root) / "index.sqlite")
    conn.execute(
        "insert into commands(command, exit_code, duration_ms, stdout_bytes, stderr_bytes, output_path) values(?,?,?,?,?,?)",
        (" ".join(argv), proc.returncode, duration_ms, summary["stdout_bytes"], summary["stderr_bytes"], summary_path.as_posix()),
    )
    increment(conn, "commands_intercepted", 1)
    increment(conn, "raw_output_bytes", summary["stdout_bytes"] + summary["stderr_bytes"])
    increment(conn, "compact_output_bytes", len(json.dumps(summary).encode()))
    conn.commit()
    raw_bytes = summary["stdout_bytes"] + summary["stderr_bytes"]
    if raw_bytes <= 4096:
        if proc.stdout:
            print(proc.stdout, end="")
        if proc.stderr:
            print(proc.stderr, end="", file=sys.stderr)
        return proc.returncode
    print("ContextGuard capture summary")
    print(f"command: {' '.join(argv)}")
    print(f"exit_code: {proc.returncode}")
    print(f"duration_ms: {duration_ms}")
    print(f"raw_bytes: {raw_bytes}")
    for line in summary["summary_lines"]:
        print(line)
    print(f"full_output: {summary_path}")
    return proc.returncode
