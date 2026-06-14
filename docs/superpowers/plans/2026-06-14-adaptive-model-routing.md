# Adaptive Model Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Install and enforce a conservative one-worker GPT-5.4-mini routing workflow under a higher-capability main Codex model.

**Architecture:** Add a deterministic routing classifier and custom-agent renderer, inject concise routing context through existing project guidance, and observe subagent lifecycle events. Validate with isolated Codex parent/worker runs and hidden behavioral tests.

**Tech Stack:** Python 3, pytest, Codex project custom agents, lifecycle hooks, JSON telemetry.

---

### Task 1: Routing Classifier

**Files:**
- Create: `contextguard/contextguard/model_router.py`
- Create: `contextguard/tests/test_model_router.py`

- [ ] Add failing tests for eligible bounded implementation, trivial-task avoidance and high-risk exclusions.
- [ ] Run focused tests and confirm failure.
- [ ] Implement deterministic routing decisions and concise directives.
- [ ] Run focused tests until green.

### Task 2: Custom Worker Installation

**Files:**
- Modify: `contextguard/contextguard/documentation.py`
- Modify: `contextguard/contextguard/onboarding.py`
- Create: `contextguard/tests/test_model_routing_installation.py`

- [ ] Add failing tests for `.codex/agents/contextguard-worker.toml` creation and preservation of unrelated agent files.
- [ ] Verify red state.
- [ ] Render a GPT-5.4-mini medium worker with non-recursive, bounded instructions.
- [ ] Verify focused tests pass.

### Task 3: Runtime Guidance And Telemetry

**Files:**
- Modify: `contextguard/hooks/user_prompt_submit.py`
- Modify: `contextguard/hooks/hooks.json`
- Create: `contextguard/hooks/subagent_start.py`
- Create: `contextguard/hooks/subagent_stop.py`
- Modify: `contextguard/contextguard/session_state.py`
- Modify: relevant hook tests.

- [ ] Add failing tests for routing context and lifecycle telemetry.
- [ ] Verify red state.
- [ ] Add automatic one-worker guidance and record subagent starts/stops without blocking execution.
- [ ] Verify hook and session tests pass.

### Task 4: Real Routing Acceptance

**Files:**
- Create: `contextguard/benchmarks/real_codex_model_routing_ab.py`
- Create: `contextguard/tests/test_real_codex_model_routing_ab.py`
- Modify: `changy.md`
- Modify: `contextguard/changy.md`

- [ ] Build a human feature/bug task with public and hidden acceptance checks.
- [ ] Run RAW GPT-5.5 and routed GPT-5.5 plus GPT-5.4-mini worker in isolated roots.
- [ ] Reject the feature unless routing is observed, quality is equal and estimated cost/limit pressure improves.
- [ ] Run full tests, package acceptance and build validation.
- [ ] Version, commit, push `main`, update the marketplace installation and refresh the active project.
