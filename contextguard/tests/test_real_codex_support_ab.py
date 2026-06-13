from pathlib import Path

from benchmarks.real_codex_support_ab import (
    PROMPT,
    RUN_ORDERS,
    apply_reference_solution,
    create_fixture,
    validate_fixture,
)


def test_support_prompt_is_ticket_driven_without_solution_requirements():
    assert "SUPPORT_TICKET.md" in PROMPT
    assert "reproduce" in PROMPT.lower()
    assert "root cause" in PROMPT.lower()
    assert "threading.RLock" not in PROMPT
    assert "schema version 2" not in PROMPT


def test_three_runs_counterbalance_execution_order():
    assert RUN_ORDERS == [("raw", "contextguard"), ("contextguard", "raw"), ("raw", "contextguard")]


def test_hidden_acceptance_fails_before_fix_and_passes_reference(tmp_path: Path):
    project = create_fixture(tmp_path / "fixture")
    before = validate_fixture(project)
    assert before["exit_code"] != 0
    assert before["hidden_failed_tests"] > 0

    apply_reference_solution(project)
    after = validate_fixture(project)
    assert after["exit_code"] == 0
    assert after["hidden_passed_tests"] == 144
    assert after["canonical_output"]["status"] == "reserved"


def test_agent_repository_does_not_contain_hidden_tests(tmp_path: Path):
    project = create_fixture(tmp_path / "fixture")
    files = {path.name for path in project.rglob("*.py")}
    assert "test_hidden_acceptance.py" not in files
    assert (project / "SUPPORT_TICKET.md").exists()
    assert not (project / "SPEC.md").exists()


def test_each_trial_uses_a_separate_temporary_root():
    source = (Path(__file__).resolve().parents[1] / "benchmarks/real_codex_support_ab.py").read_text()
    assert 'prefix=f"contextguard-support-ab-{index}-{kind}-"' in source
