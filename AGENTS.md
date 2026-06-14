# Project Instructions

<!-- BEGIN CONTEXTGUARD MANAGED SECTION -->
ContextGuard policy: Adaptive Maximum Efficiency.

- Reuse unchanged reads; group repeated inspection; expand as needed.
- For tests, linters, builds; recursive listings or searches; `git diff`; or structured data or logs, run `.contextguard/bin/contextguard capture -- <command>` before stdout reaches Codex (`sh -lc`). This protects non-interactive runs and does not depend on lifecycle hook dispatch.
- Enforcement: Never run `sed`, `tail`, `head`, `cat`, `awk`, `jq`, or `rg` directly on logs, structured data, generated output, artifacts, or multiple files. Prefix the complete command with `.contextguard/bin/contextguard capture --`. Pipelines do not make output safe; wrap the whole pipeline. Small, bounded source reads of one file may run directly.
- Do not narrate routine inspection or tool use, restate intent, echo source, or print unasked diffs.
- Final responses: changed files, validation, and only real risks.
- Never trade correctness, context, validation, security, or data integrity for brevity.

Project: existing.
<!-- END CONTEXTGUARD MANAGED SECTION -->
