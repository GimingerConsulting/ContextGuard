from __future__ import annotations

import hashlib
import os
import re
import shutil
from pathlib import Path
from typing import Iterable


IGNORED_DIRS = {
    ".git",
    ".contextguard",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".next",
    ".venv",
    "venv",
    "vendor",
}


def safe_relpath(path: Path, root: Path) -> str:
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    if resolved_path != resolved_root and resolved_root not in resolved_path.parents:
        raise ValueError(f"path escapes project root: {path}")
    return resolved_path.relative_to(resolved_root).as_posix()


def is_binary(path: Path, sample_size: int = 4096) -> bool:
    try:
        sample = path.read_bytes()[:sample_size]
    except OSError:
        return True
    return b"\0" in sample


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def estimate_tokens(text: str) -> int:
    return max(1, (len(text) + 3) // 4)


def find_executable(name: str) -> str | None:
    return shutil.which(name)


def iter_project_files(root: Path) -> Iterable[Path]:
    for current, dirs, files in os.walk(root):
        current_path = Path(current)
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".git")]
        for file_name in files:
            path = current_path / file_name
            if path.is_symlink() or not path.is_file():
                continue
            yield path


def extract_error_lines(text: str, limit: int = 20) -> list[str]:
    patterns = re.compile(r"\b(error|failed|failure|traceback|exception|warning)\b", re.I)
    seen: set[str] = set()
    result: list[str] = []
    for line in text.splitlines():
        compact = line.strip()
        if not compact or not patterns.search(compact):
            continue
        signature = re.sub(r"\d+", "N", compact)[:240]
        if signature in seen:
            continue
        seen.add(signature)
        result.append(compact[:500])
        if len(result) >= limit:
            break
    return result
