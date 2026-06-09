from pathlib import Path

from contextguard.project import detect_project


def test_empty_project_initialization(tmp_path: Path):
    info = detect_project(tmp_path)
    assert info.kind == "empty"


def test_existing_python_project(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
    (tmp_path / "app.py").write_text("print('x')\n")
    info = detect_project(tmp_path)
    assert info.kind in {"new-partial", "existing"}


def test_monorepo_detection(tmp_path: Path):
    (tmp_path / "pnpm-workspace.yaml").write_text("packages: []\n")
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "package.json").write_text("{}\n")
    assert detect_project(tmp_path).is_monorepo
