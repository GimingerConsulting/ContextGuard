from __future__ import annotations

import json
from pathlib import Path


def detect_repo_facts(root: Path) -> dict:
    facts = {
        "languages": [],
        "package_managers": [],
        "tests": [],
        "entry_points": [],
        "config_files": [],
    }
    suffixes = {p.suffix.lower() for p in root.rglob("*") if p.is_file() and ".contextguard" not in p.parts}
    if ".py" in suffixes:
        facts["languages"].append("Python")
    if ".js" in suffixes or ".ts" in suffixes or ".tsx" in suffixes:
        facts["languages"].append("JavaScript/TypeScript")
    markers = {
        "package.json": "npm",
        "pnpm-lock.yaml": "pnpm",
        "yarn.lock": "yarn",
        "pyproject.toml": "Python packaging",
        "requirements.txt": "pip",
    }
    for marker, label in markers.items():
        if (root / marker).exists():
            facts["package_managers"].append(label)
            facts["config_files"].append(marker)
    package_json = root / "package.json"
    if package_json.exists():
        try:
            scripts = json.loads(package_json.read_text(encoding="utf-8")).get("scripts", {})
            facts["tests"].extend(f"npm run {name}" for name in scripts if "test" in name)
            facts["entry_points"].extend(str(v) for k, v in scripts.items() if k in {"start", "dev"})
        except Exception:
            pass
    if (root / "pytest.ini").exists() or (root / "tests").exists():
        facts["tests"].append("python -m pytest")
    return facts
