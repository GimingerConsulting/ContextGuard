# Real Codex Hard A/B Benchmark Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and run a reproducible real-Codex benchmark comparing raw and ContextGuard-assisted completion of the same difficult coding task.

**Architecture:** A Python harness creates identical committed fixture repositories, prepares isolated Codex homes, initializes only the optimized copy, executes both agents through JSONL mode, parses exact usage events, validates both results, and writes a machine-readable report. Fixture generation and result parsing remain deterministic and unit tested; actual model runs are opt-in because they consume account quota and time.

**Tech Stack:** Python 3.10+, pytest, git, Codex CLI JSONL, ContextGuard hooks.

---

### Task 1: Benchmark Contract Tests

**Files:**
- Create: `contextguard/tests/test_real_codex_ab.py`
- Create: `contextguard/benchmarks/real_codex_ab.py`

- [ ] Write tests asserting the fixture starts with failing feature tests, contains more than 100 collected cases, and becomes fully valid after applying the reference implementation.
- [ ] Write tests for parsing `turn.completed` token usage, command-output bytes, file changes, and final messages from JSONL.
- [ ] Run `python3 -m pytest tests/test_real_codex_ab.py -q`; expect import or missing-function failures.
- [ ] Implement fixture generation, reference patch support, JSONL parsing, validation, and repository hashing.
- [ ] Re-run the focused test; expect all tests to pass.

### Task 2: Controlled Codex Runner

**Files:**
- Modify: `contextguard/benchmarks/real_codex_ab.py`
- Test: `contextguard/tests/test_real_codex_ab.py`

- [ ] Add a failing test for command construction parity between raw and optimized runs.
- [ ] Implement isolated `CODEX_HOME` creation, authentication copying, fixed model/reasoning/sandbox settings, timeout handling, and exact elapsed-time measurement.
- [ ] Implement optimized project initialization and current-schema project hooks.
- [ ] Re-run focused tests; expect all tests to pass.

### Task 3: Real A/B Execution and Report

**Files:**
- Create: `contextguard/benchmarks/results/real-codex-hard-ab-2026-06-10.json`
- Modify: `contextguard/benchmarks/README.md`
- Modify: `changy.md`
- Modify: `contextguard/changy.md`

- [ ] Run the raw trial and preserve its JSONL, final response, stderr, repository diff, validation output, and usage.
- [ ] Run the ContextGuard trial with the same prompt and preserve the same artifacts.
- [ ] Validate both repositories with the complete hidden suite and canonical scenario command.
- [ ] Generate the comparison JSON with absolute values and percentage differences.
- [ ] Document measured results, equivalence status, limitations, and any benchmark problems with solutions.

### Task 4: Verification and Delivery

**Files:**
- Review all changed files.

- [ ] Run `python3 -m pytest -q`; expect the complete ContextGuard suite to pass.
- [ ] Run `git diff --check`; expect no whitespace errors.
- [ ] Confirm result artifacts contain no authentication data or temporary absolute paths that expose secrets.
- [ ] Commit the harness, tests, design, plan, result summary, and protocol updates.
- [ ] Push `main` to `origin`.
