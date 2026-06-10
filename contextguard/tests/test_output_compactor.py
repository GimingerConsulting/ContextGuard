from contextguard.output_compactor import compact_output


def test_repeated_log_error_deduplication():
    output = "\n".join(["ERROR item 1 failed", "ERROR item 2 failed", "ok"])
    compact = compact_output(output, "")
    assert len(compact["errors"]) == 1
    assert compact["line_count"] == 3


def test_one_line_large_output_is_clipped():
    compact = compact_output("x" * 10_000, "")
    assert len(compact["summary_lines"][0]) < 600
    assert "truncated" in compact["summary_lines"][0]


def test_compact_output_records_shown_bytes():
    compact = compact_output("ERROR one\nERROR two\n")
    assert compact["compact_bytes"] > 0
    assert compact["raw_bytes"] > compact["compact_bytes"]


def test_compact_output_separates_unique_failures_warnings_and_tests():
    output = """FAILED tests/test_index.py::test_cache - AssertionError: bad hash
FAILED tests/test_index.py::test_cache - AssertionError: bad hash 2
WARNING deprecated option
Traceback (most recent call last):
  File \"app.py\", line 12, in run
ValueError: broken
2 failed, 4 passed in 1.20s
"""
    compact = compact_output(output)
    assert compact["failed_tests"] == ["tests/test_index.py::test_cache"]
    assert compact["warnings"] == ["WARNING deprecated option"]
    assert len(compact["errors"]) == 2
    assert compact["test_summary"] == "2 failed, 4 passed in 1.20s"
    assert compact["stack_traces"]
