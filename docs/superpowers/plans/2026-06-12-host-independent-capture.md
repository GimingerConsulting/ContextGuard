# Host-Independent Capture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Guarantee that noisy command output is compact before it reaches Codex, without relying on lifecycle hook replacement behavior.

**Architecture:** Generate a project-local launcher during initialization and instruct Codex through the managed `AGENTS.md` policy to execute noisy commands through it. Keep hooks as optional defense in depth and require runner evidence in acceptance and real A/B benchmarks.

**Tech Stack:** Python standard library, pytest, Codex CLI JSONL benchmarks, Markdown project instructions.

---

### Task 1: Project-Local Runner

**Files:**
- Create: `contextguard/contextguard/project_runner.py`
- Modify: `contextguard/contextguard/onboarding.py`
- Modify: `contextguard/contextguard/cli.py`
- Test: `contextguard/tests/test_cli_flows.py`

- [ ] Add failing tests requiring setup and refresh to create an executable `.contextguard/bin/contextguard` runner that works from paths containing spaces.
- [ ] Run the focused tests and confirm failure because the runner does not exist.
- [ ] Generate an idempotent launcher that imports the current installed package root and calls `contextguard.cli.main`.
- [ ] Run focused tests and verify runner execution, exit-code preservation and refresh regeneration.

### Task 2: Managed Execution Policy

**Files:**
- Modify: `contextguard/contextguard/output_policy.py`
- Test: `contextguard/tests/test_documentation_safety.py`

- [ ] Add failing tests requiring explicit project-runner commands, noisy-command categories, shell fallback and correctness language in the managed policy.
- [ ] Run focused tests and confirm the policy assertions fail.
- [ ] Update the compact managed policy without weakening correctness or validation requirements.
- [ ] Run focused tests and enforce a bounded policy size.

### Task 3: Readiness And Metrics

**Files:**
- Modify: `contextguard/contextguard/cli.py`
- Modify: `contextguard/contextguard/metrics.py`
- Test: `contextguard/tests/test_cli_flows.py`

- [ ] Add failing tests for separate host-independent runner readiness and optional hook status.
- [ ] Implement truthful setup, status and report output.
- [ ] Verify focused CLI tests.

### Task 4: Installed Acceptance And Real A/B

**Files:**
- Modify: `contextguard/benchmarks/install_acceptance.py`
- Modify: `contextguard/benchmarks/real_codex_ab.py`
- Modify: `contextguard/tests/test_install_acceptance.py`
- Modify: `contextguard/tests/test_real_codex_ab.py`

- [ ] Add failing acceptance assertions proving the isolated installed runner is executed and reduces visible output.
- [ ] Update the real benchmark prompt and acceptance gates so optimized runs must execute `.contextguard/bin/contextguard capture`.
- [ ] Run focused benchmark tests and isolated acceptance.
- [ ] Run the opt-in real Codex A/B and accept only equal validated results with observed runner execution.

### Task 5: Release And Documentation

**Files:**
- Modify: `contextguard/.codex-plugin/plugin.json`
- Modify: `contextguard/pyproject.toml`
- Modify: `contextguard/README.md`
- Modify: `contextguard/CHANGELOG.md`
- Modify: `changy.md`

- [ ] Bump the release to `0.3.0` and document host-independent execution protection and honest limitations.
- [ ] Run the complete test suite, plugin validation and benchmarks.
- [ ] Commit and push only task changes to `main`.
- [ ] Update the installed ContextGuard plugin and rerun setup in this repository.
