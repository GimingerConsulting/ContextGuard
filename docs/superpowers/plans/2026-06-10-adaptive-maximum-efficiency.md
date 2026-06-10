# Adaptive Maximum Efficiency Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make output efficiency a first-class ContextGuard capability while preserving validation quality and reducing ContextGuard's own overhead.

**Architecture:** Add one deterministic output-policy source that renders managed Codex guidance and validates final-response semantics. Extend command compaction with structured failures, warnings, tests, signatures, and local full-output paths. Tighten task capsules around cached repository/session facts, then extend metrics and benchmarks to compare equivalent outcomes rather than byte reduction alone.

**Tech Stack:** Python 3.10+, SQLite, pytest, Codex lifecycle hooks, Markdown documentation.

---

### Task 1: Output Policy and Managed Guidance

**Files:**
- Create: `contextguard/contextguard/output_policy.py`
- Modify: `contextguard/contextguard/documentation.py`
- Modify: `contextguard/hooks/session_start.py`
- Test: `contextguard/tests/test_output_policy.py`
- Test: `contextguard/tests/test_documentation_safety.py`

- [ ] Write failing tests for task complexity, routine narration suppression, source/diff echo prevention, concise final responses, retained failures/risks/validation, and explicit detail overrides.
- [ ] Run `python3 -m pytest tests/test_output_policy.py tests/test_documentation_safety.py -q`; expect failures for the missing policy module and old policy name.
- [ ] Implement immutable policy rules, semantic response inspection, and one compact managed-instruction renderer using `Adaptive Maximum Efficiency`.
- [ ] Make initialized session startup silent and render project guidance from the single policy source.
- [ ] Re-run the focused tests; expect all to pass.

### Task 2: Structured Tool-Output Efficiency

**Files:**
- Modify: `contextguard/contextguard/output_compactor.py`
- Modify: `contextguard/contextguard/output_capture.py`
- Modify: `contextguard/hooks/post_tool_use.py`
- Test: `contextguard/tests/test_output_compactor.py`
- Test: `contextguard/tests/test_cli_flows.py`
- Test: `contextguard/tests/test_hooks.py`

- [ ] Write failing tests for unique errors, unique warnings, failed test names, stack-trace retention, exit code, duration, total bytes, and full-output paths.
- [ ] Run the focused tests and confirm the new assertions fail against the current head/error/tail summary.
- [ ] Implement deterministic signature grouping and a compact structured renderer without arbitrary loss of unique failures.
- [ ] Store complete stdout/stderr and JSON summaries under `.contextguard/tmp/`, preserving non-zero exits.
- [ ] Re-run focused tests; expect all to pass.

### Task 3: Progressive Context and Session Reuse

**Files:**
- Modify: `contextguard/contextguard/database.py`
- Modify: `contextguard/contextguard/index.py`
- Modify: `contextguard/contextguard/task_classifier.py`
- Modify: `contextguard/contextguard/context_capsule.py`
- Modify: `contextguard/hooks/user_prompt_submit.py`
- Modify: `contextguard/hooks/pre_compact.py`
- Test: `contextguard/tests/test_task_classifier.py`
- Test: `contextguard/tests/test_context_capsule.py`
- Test: `contextguard/tests/test_hooks.py`

- [ ] Write failing tests for progressive retrieval levels, ambiguous-result escalation, unchanged-index reuse, cached session facts, and capsule limits below 300/400 estimated tokens.
- [ ] Run focused tests; expect failures for missing retrieval/escalation/session fields.
- [ ] Add deterministic relevance scoring and only emit file/symbol recommendations above a reliable confidence threshold.
- [ ] Persist compact verified session facts and reuse them without re-reading unchanged files.
- [ ] Re-run focused tests; expect all to pass.

### Task 4: Metrics and Same-Result Benchmarks

**Files:**
- Modify: `contextguard/contextguard/metrics.py`
- Modify: `contextguard/contextguard/cli.py`
- Modify: `contextguard/benchmarks/run_benchmarks.py`
- Modify: `contextguard/benchmarks/README.md`
- Test: `contextguard/tests/test_benchmarks.py`
- Test: `contextguard/tests/test_cli_flows.py`

- [ ] Write failing tests for policy overhead, net reduction, repeated reads, inspected files, tool calls, equivalent exit/result hashes, and semantic final-response assertions.
- [ ] Run focused tests and confirm the old seven-fixture byte-only schema fails them.
- [ ] Extend metrics and benchmark records with measured versus estimated labels and same-result acceptance criteria.
- [ ] Add the required trivial, medium, debugging, verbose-output, structured-data, repeated-error, long-session, restart, partial-change, and large-repository scenarios.
- [ ] Re-run focused tests; expect all to pass.

### Task 5: Documentation and Migration

**Files:**
- Modify: `contextguard/README.md`
- Modify: `README.md`
- Modify: `contextguard/CHANGELOG.md`
- Modify: `contextguard/skills/contextguard-init/references/AGENTS.template.md`
- Modify: `contextguard/skills/contextguard-init/references/ARCHITECTURE.template.md`
- Modify: `contextguard/skills/contextguard-init/references/CURRENT_STATE.template.md`
- Modify: `changy.md`
- Modify: `contextguard/changy.md`

- [ ] Replace stale `Adaptive Maximum Savings` wording with `Adaptive Maximum Efficiency`.
- [ ] Document the required product statement, scope, quality floor, local output storage, progressive retrieval, and benchmark methodology.
- [ ] Record audit findings, implementation changes, validation, limitations, and solutions in both change protocol files.
- [ ] Run documentation safety tests; expect all to pass without universal savings claims.

### Task 6: Full Verification and Delivery

**Files:**
- Review all changed files.

- [ ] Run `python3 -m pytest -q` from `contextguard/`; expect the complete suite to pass.
- [ ] Run `python3 benchmarks/run_benchmarks.py`; expect valid JSON and equivalent baseline/optimized outcomes.
- [ ] Run `git diff --check`; expect no whitespace errors.
- [ ] Review `git diff --stat` and targeted diffs for unrelated changes; leave existing `.DS_Store` files untouched.
- [ ] Commit the implementation on `main` and push `main` to `origin`.
