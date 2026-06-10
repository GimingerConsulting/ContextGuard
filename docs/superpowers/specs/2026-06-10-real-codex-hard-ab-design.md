# Real Codex Hard A/B Benchmark Design

## Objective

Measure real Codex CLI input tokens, cached input tokens, output tokens, reasoning tokens, tool-output bytes, wall time, validation quality, and repository-state equivalence for the same difficult coding task with and without ContextGuard.

## Controlled Environment

- Model: `gpt-5.5`.
- Reasoning: `medium`.
- Codex CLI: non-interactive `codex exec --json`.
- Separate temporary `CODEX_HOME` directories copy only authentication from the user's home.
- Separate repositories start from byte-identical fixtures and commits.
- Both runs use the same prompt, sandbox, approval policy, model, reasoning, and timeout.
- The raw repository has no ContextGuard state, guidance, or hooks.
- The optimized repository is initialized with the current ContextGuard source and uses vetted project-local hooks.

## Hard Task

The fixture is a multi-module Python settlement and reconciliation service. The requested feature requires coordinated changes across allocation, currency conversion, idempotency, ledger posting, audit output, and CLI behavior. Hidden validation includes more than 100 parameterized cases and intentionally verbose failure output. Large irrelevant logs and datasets are present to create realistic context pressure without making them necessary for correctness.

The agent must implement deterministic partial-settlement handling with banker-safe decimal rounding, duplicate-event rejection, account-level caps, stable audit ordering, and backward compatibility. The prompt specifies behavior but not file locations.

## ContextGuard Activation

The optimized copy runs `contextguard init`, then installs `.codex/hooks.json` pointing at the current ContextGuard hooks. Hook trust is bypassed only for this controlled benchmark invocation. The raw copy receives no generated `AGENTS.md` or ContextGuard state.

## Measurements

- Exact token usage from the final `turn.completed.usage` JSON event.
- Wall-clock duration around the complete `codex exec` process.
- Command-output bytes from completed command-execution events.
- Number of command executions and file changes.
- Final response bytes.
- Validation exit code, passed/failed test counts, canonical scenario output, and repository hash.

## Acceptance

The comparison is valid only when both runs complete the requested behavior, pass the same validation, and produce the same canonical output. Repository diffs may differ structurally, but functional validation must be identical. Any failed, timed-out, or non-equivalent trial is reported as invalid rather than counted as a ContextGuard win.

## Interpretation

Exact tokens and wall time are measured. Results remain one controlled sample because model behavior is stochastic. Cached input is reported separately, and both total input and uncached input are compared. No universal savings claim is derived from one run.
