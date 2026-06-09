from pathlib import Path

from contextguard.command_rewriter import rewrite_for_capture


def test_rewrite_quotes_shell_command():
    rewritten = rewrite_for_capture("cat 'file with spaces.txt'")
    assert rewritten is not None
    assert "contextguard capture -- sh -c" in rewritten
    assert "file with spaces.txt" in rewritten


def test_no_rewrite_when_unsafe_or_small():
    assert rewrite_for_capture("pwd") is None


def test_rewrite_can_use_absolute_runner_with_spaces():
    runner = Path("/tmp/path with spaces/contextguard")
    rewritten = rewrite_for_capture("find .", runner)
    assert rewritten is not None
    assert "'/tmp/path with spaces/contextguard'" in rewritten
