from contextguard.command_rewriter import rewrite_for_capture


def test_rewrite_quotes_shell_command():
    rewritten = rewrite_for_capture("cat 'file with spaces.txt'")
    assert rewritten is not None
    assert "contextguard capture -- sh -c" in rewritten
    assert "file with spaces.txt" in rewritten


def test_no_rewrite_when_unsafe_or_small():
    assert rewrite_for_capture("pwd") is None
