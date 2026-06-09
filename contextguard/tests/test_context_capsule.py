from pathlib import Path

from contextguard.context_capsule import build_capsule
from contextguard.utils import estimate_tokens


def test_task_capsule_limit(tmp_path: Path):
    for index in range(50):
        (tmp_path / f"payment_{index}.py").write_text("x=1\n")
    capsule = build_capsule(tmp_path, "payment bug", token_limit=80)
    assert estimate_tokens(capsule) <= 80
    assert "ContextGuard task capsule" in capsule
