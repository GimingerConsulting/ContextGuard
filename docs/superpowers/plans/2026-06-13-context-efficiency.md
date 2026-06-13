# Context Efficiency Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add safe session checkpoints, hash-aware repeated-read detection, and a non-blocking command-budget advisor without changing the user's model.

**Architecture:** A new session-state module persists versioned transient observations and durable checkpoints. A focused advisor module classifies read-only commands and command families, while existing lifecycle hooks reset, consult, and update this state.

**Tech Stack:** Python 3.9+, JSON state files, SHA-256, pytest, Codex lifecycle hooks.

---

### Task 1: Session State And Checkpoints

**Files:**
- Create: `contextguard/contextguard/session_state.py`
- Modify: `contextguard/contextguard/context_capsule.py`
- Test: `contextguard/tests/test_session_state.py`
- Test: `contextguard/tests/test_context_capsule.py`

- [ ] Write failing tests for session reset retaining checkpoints, allow-listed checkpoint persistence, and compact resume rendering.
- [ ] Run the focused tests and confirm failures are caused by missing APIs.
- [ ] Implement atomic versioned state persistence and checkpoint helpers.
- [ ] Run the focused tests and confirm they pass.

### Task 2: Hash-Aware Read Reuse

**Files:**
- Create: `contextguard/contextguard/optimization_advisor.py`
- Modify: `contextguard/contextguard/session_state.py`
- Test: `contextguard/tests/test_optimization_advisor.py`

- [ ] Write failing tests for exact repeated `cat`/`sed -n` reads, changed-file invalidation, missing files, and unsupported commands.
- [ ] Run the focused tests and confirm expected failures.
- [ ] Implement safe command parsing, project-relative file resolution, SHA-256 snapshots, and repeated-read advice.
- [ ] Run the focused tests and confirm they pass.

### Task 3: Command Budget

**Files:**
- Modify: `contextguard/contextguard/optimization_advisor.py`
- Modify: `contextguard/contextguard/session_state.py`
- Test: `contextguard/tests/test_optimization_advisor.py`

- [ ] Write failing tests for repeated full-suite validation, repeated repository inspection, command milestones, advice deduplication, and targeted-test exemptions.
- [ ] Run the focused tests and confirm expected failures.
- [ ] Implement normalized command families and advisory thresholds without command denial.
- [ ] Run the focused tests and confirm they pass.

### Task 4: Lifecycle Hook Integration

**Files:**
- Modify: `contextguard/hooks/session_start.py`
- Modify: `contextguard/hooks/pre_tool_use.py`
- Modify: `contextguard/hooks/post_tool_use.py`
- Modify: `contextguard/hooks/pre_compact.py`
- Test: `contextguard/tests/test_hooks.py`

- [ ] Write failing hook tests for session reset, advisory PreToolUse envelopes, successful command recording, and checkpoint creation.
- [ ] Run the focused hook tests and confirm expected failures.
- [ ] Integrate state reset, pre-command advice, post-command recording, and checkpoint persistence.
- [ ] Run the focused hook tests and confirm they pass.

### Task 5: CLI, Documentation, And Verification

**Files:**
- Modify: `contextguard/contextguard/cli.py`
- Modify: `contextguard/contextguard/documentation.py`
- Modify: `contextguard/README.md`
- Modify: `contextguard/CHANGELOG.md`
- Modify: `contextguard/changy.md`
- Modify: `changy.md`

- [ ] Add status fields for session commands, avoided repeated reads, and emitted budget advice.
- [ ] Document behavior, safety boundaries, and the absence of model selection.
- [ ] Run focused tests, then the complete test suite and benchmark acceptance.
- [ ] Commit the implementation, push `main`, update the installed plugin, and require a Codex restart before live A/B testing.
