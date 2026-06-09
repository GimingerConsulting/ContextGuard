import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_cli(args: list[str], cwd: Path):
    return subprocess.run(
        [sys.executable, "-m", "contextguard.cli", *args],
        cwd=cwd,
        env={"PYTHONPATH": str(ROOT)},
        text=True,
        capture_output=True,
    )


def test_init_repeated_status_and_paths_with_spaces(tmp_path: Path):
    project = tmp_path / "project with spaces"
    project.mkdir()
    (project / "package.json").write_text('{"scripts":{"test":"echo ok"}}\n')
    first = run_cli(["init"], project)
    second = run_cli(["init"], project)
    status = run_cli(["status"], project)
    assert first.returncode == 0
    assert second.returncode == 0
    assert status.returncode == 0
    assert "ContextGuard: active" in status.stdout
    assert "Last refresh: unknown" not in status.stdout
    assert (project / ".contextguard" / "index.sqlite").exists()


def test_capture_preserves_non_zero_exit_code(tmp_path: Path):
    result = run_cli(["capture", "--", sys.executable, "-c", "print('bad'); raise SystemExit(7)"], tmp_path)
    assert result.returncode == 7
    assert result.stdout == "bad\n"
    assert list((tmp_path / ".contextguard" / "tmp").glob("*.summary.json"))


def test_uninstall_requires_confirmation(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    run_cli(["init"], project)
    dry = run_cli(["uninstall-project"], project)
    assert dry.returncode == 0
    assert (project / ".contextguard").exists()
    confirmed = run_cli(["uninstall-project", "--yes"], project)
    assert confirmed.returncode == 0
    assert not (project / ".contextguard").exists()
