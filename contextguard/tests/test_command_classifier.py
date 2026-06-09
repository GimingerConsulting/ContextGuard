from contextguard.command_classifier import classify_command


def test_small_command_passthrough():
    assert classify_command("pwd").action == "allow"


def test_large_commands_captured():
    assert classify_command("cat huge.log").action == "capture"
    assert classify_command("git diff").action == "capture"
    assert classify_command("find .").action == "capture"


def test_destructive_commands_not_rewritten():
    decision = classify_command("rm -rf build")
    assert decision.action == "allow"
    assert "not rewritten" in decision.reason
