from pathlib import Path

from contextguard.documentation import replace_managed_section
from contextguard.config import MANAGED_BEGIN, MANAGED_END


def test_existing_agents_preservation_and_backup(tmp_path: Path):
    path = tmp_path / "AGENTS.md"
    path.write_text("# User\n\nKeep this.\n")
    changed = replace_managed_section(path, "Project Instructions", "managed")
    assert changed
    text = path.read_text()
    assert "Keep this." in text
    assert MANAGED_BEGIN in text and MANAGED_END in text
    assert list(tmp_path.glob("AGENTS.md.contextguard-backup-*"))


def test_managed_section_replacement(tmp_path: Path):
    path = tmp_path / "AGENTS.md"
    replace_managed_section(path, "Project Instructions", "first")
    replace_managed_section(path, "Project Instructions", "second")
    text = path.read_text()
    assert "second" in text
    assert "first" not in text
