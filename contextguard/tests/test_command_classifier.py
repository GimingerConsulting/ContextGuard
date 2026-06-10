from contextguard.command_classifier import classify_command


def test_small_command_passthrough():
    assert classify_command("pwd").action == "allow"


def test_large_commands_captured():
    assert classify_command("cat huge.log").action == "capture"
    assert classify_command("git diff").action == "capture"
    assert classify_command("find .").action == "capture"


def test_python_module_validation_and_tee_pipeline_are_captured():
    assert classify_command("python3 -m pytest -q").action == "capture"
    assert classify_command("python -m pytest -q 2>&1 | tee /tmp/tests.log").action == "capture"


def test_destructive_commands_not_rewritten():
    decision = classify_command("rm -rf build")
    assert decision.action == "allow"
    assert "not rewritten" in decision.reason
