from pathlib import Path

from contextguard.context_capsule import build_capsule, build_session_capsule, persist_session_capsule
from contextguard.utils import estimate_tokens


def test_task_capsule_limit(tmp_path: Path):
    for index in range(50):
        (tmp_path / f"payment_{index}.py").write_text("x=1\n")
    capsule = build_capsule(tmp_path, "payment bug", token_limit=80)
    assert estimate_tokens(capsule) <= 80
    assert "ContextGuard capsule" in capsule


def test_high_confidence_capsule_is_short(tmp_path: Path):
    (tmp_path / "billing_service.py").write_text("class BillingService:\n    pass\n")
    capsule = build_capsule(tmp_path, "fix BillingService")
    assert len(capsule.encode()) < 260


def test_high_confidence_capsule_stays_compact_with_many_matches(tmp_path: Path):
    for index in range(25):
        (tmp_path / f"subscription_billing_{index}.py").write_text(
            f"class SubscriptionBilling{index}:\n    pass\n"
        )
    capsule = build_capsule(tmp_path, "fix subscription billing")
    assert len(capsule.encode()) < 300


def test_normal_task_capsule_stays_below_300_estimated_tokens(tmp_path: Path):
    (tmp_path / "billing.py").write_text("class BillingService:\n    pass\n")
    capsule = build_capsule(tmp_path, "fix BillingService")
    assert estimate_tokens(capsule) < 300


def test_session_capsule_keeps_only_verified_resume_facts(tmp_path: Path):
    facts = {
        "current_objective": "finish output policy",
        "changed_files": ["contextguard/output_policy.py"],
        "verified_tests": ["12 tests passed"],
        "known_failures": [],
        "active_constraints": ["preserve correctness"],
        "next_action": "run full suite",
        "ignored_blob": "x" * 20_000,
    }
    persist_session_capsule(tmp_path, facts)
    capsule = build_session_capsule(tmp_path)
    assert "finish output policy" in capsule
    assert "ignored_blob" not in capsule
    assert estimate_tokens(capsule) < 400


def test_session_capsule_renders_versioned_checkpoint_without_metadata_noise(tmp_path: Path):
    persist_session_capsule(
        tmp_path,
        {"current_objective": "resume efficiently", "next_action": "run focused test"},
    )

    capsule = build_session_capsule(tmp_path)

    assert "resume efficiently" in capsule
    assert "checkpoint_id=" not in capsule
    assert "version=" not in capsule
