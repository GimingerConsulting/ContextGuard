from contextguard.output_compactor import compact_output


def test_repeated_log_error_deduplication():
    output = "\n".join(["ERROR item 1 failed", "ERROR item 2 failed", "ok"])
    compact = compact_output(output, "")
    assert len(compact["errors"]) == 1
    assert compact["line_count"] == 3
