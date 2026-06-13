from pathlib import Path

from contextguard.session_state import (
    load_session_state,
    persist_checkpoint,
    reset_session_state,
)


def test_session_reset_keeps_latest_checkpoint_but_clears_transient_history(tmp_path: Path):
    persist_checkpoint(tmp_path, {"current_objective": "finish optimizer", "ignored": "secret"})
    state = load_session_state(tmp_path)
    state["commands"] = [{"command": "rg --files", "family": "repository_listing"}]
    state["reads"] = {"abc": {"hashes": {"app.py": "123"}}}
    from contextguard.session_state import save_session_state

    save_session_state(tmp_path, state)
    reset_session_state(tmp_path)

    reset = load_session_state(tmp_path)
    assert reset["commands"] == []
    assert reset["reads"] == {}
    assert reset["checkpoint"]["current_objective"] == "finish optimizer"
    assert "ignored" not in reset["checkpoint"]


def test_checkpoint_is_versioned_and_allow_listed(tmp_path: Path):
    checkpoint = persist_checkpoint(
        tmp_path,
        {
            "current_objective": "ship feature",
            "changed_files": ["contextguard/session_state.py"],
            "verified_tests": ["19 passed"],
            "next_action": "run full suite",
            "transcript": "must not persist",
        },
    )

    assert checkpoint["version"] == 1
    assert checkpoint["current_objective"] == "ship feature"
    assert "transcript" not in checkpoint
    assert checkpoint["checkpoint_id"]
