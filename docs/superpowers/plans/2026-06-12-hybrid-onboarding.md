# ContextGuard Hybrid Onboarding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Automatically initialize ContextGuard in empty and existing projects after hook trust, with a one-command setup and diagnostic fallback.

**Architecture:** Extract idempotent initialization into a service shared by CLI and hooks. Persist lightweight hook heartbeats locally, expose their state through setup/status, and document the exact marketplace install, trust, restart, and smoke-test path.

**Tech Stack:** Python 3.10+, Codex lifecycle hooks, pytest, JSON/Markdown plugin metadata.

---

### Task 1: Automatic Initialization Service

**Files:**
- Create: `contextguard/contextguard/onboarding.py`
- Modify: `contextguard/contextguard/cli.py`
- Test: `contextguard/tests/test_cli_flows.py`

- [ ] Add failing tests for idempotent setup in empty and existing projects.
- [ ] Run the focused tests and confirm they fail.
- [ ] Extract initialization from `init_project` into a reusable result-returning function.
- [ ] Add the `setup` CLI command and concise setup output.
- [ ] Run the focused tests and confirm they pass.

### Task 2: Hook Auto-Init And Diagnostics

**Files:**
- Create: `contextguard/contextguard/hook_diagnostics.py`
- Modify: `contextguard/hooks/session_start.py`
- Modify: `contextguard/hooks/pre_tool_use.py`
- Modify: `contextguard/hooks/post_tool_use.py`
- Modify: `contextguard/contextguard/cli.py`
- Test: `contextguard/tests/test_hooks.py`

- [ ] Add failing tests for first-session auto-init, user-content preservation, heartbeat creation, and unverified status.
- [ ] Run the focused tests and confirm they fail.
- [ ] Implement heartbeat recording and status inspection.
- [ ] Make `SessionStart` initialize safely and record successful dispatch.
- [ ] Record PreToolUse and PostToolUse dispatch without changing their decisions.
- [ ] Run the focused tests and confirm they pass.

### Task 3: Plugin UX And Marketplace Documentation

**Files:**
- Create: `contextguard/skills/contextguard-setup/SKILL.md`
- Create: `contextguard/skills/contextguard-setup/agents/openai.yaml`
- Copy: setup skill icon assets from existing ContextGuard skills
- Modify: `contextguard/.codex-plugin/plugin.json`
- Modify: `contextguard/README.md`
- Modify: `README.md`
- Modify: `contextguard/tests/test_documentation_safety.py`

- [ ] Add failing documentation and manifest assertions for setup, `/hooks`, new-thread activation, and smoke testing.
- [ ] Run the focused tests and confirm they fail.
- [ ] Add the setup skill and marketplace starter prompt.
- [ ] Rewrite installation instructions as a numbered start-to-verification flow.
- [ ] Run documentation tests and plugin validation.

### Task 4: Acceptance, Changelog, And Publishing

**Files:**
- Modify: `contextguard/benchmarks/install_acceptance.py`
- Modify: `contextguard/tests/test_install_acceptance.py`
- Modify: `changy.md`
- Modify: `contextguard/changy.md`

- [ ] Extend isolated acceptance to begin with uninitialized projects and require SessionStart auto-init.
- [ ] Run the acceptance benchmark and full test suite.
- [ ] Record implementation, validation, limitations, and solution in both changelogs.
- [ ] Review the final diff without touching unrelated `.DS_Store` files or prior benchmark output changes.
- [ ] Commit the intended files and push `main` to GitHub.
