# Context Efficiency Design

## Goal

Increase useful Codex work per usage window without choosing models for the user or weakening validation.

## Scope

ContextGuard will add three automatic, non-blocking mechanisms:

1. Session checkpoints that preserve verified objective, files, tests, failures, constraints, and next action for compact resume context.
2. Session-scoped read fingerprints that recognize an exact repeated read only while the referenced files remain unchanged.
3. A command budget advisor that detects repeated inspection and validation patterns and recommends grouping or targeted iteration.

Model selection is explicitly out of scope and remains entirely user-controlled.

## Architecture

`session_state.py` owns a versioned JSON state file under `.contextguard/sessions/`. SessionStart resets transient read and command history while retaining the latest checkpoint. PreToolUse analyzes commands before execution and returns advisory context without denying permission. PostToolUse records successful command observations and validation facts. PreCompact writes a checkpoint using only allow-listed facts.

Repeated-read advice is emitted only for parseable, read-only `cat` or `sed -n` commands whose exact command signature was already observed in the current session and whose file SHA-256 values are unchanged. Any missing or changed file invalidates reuse. The original command remains allowed.

Command-budget advice uses normalized command families. It warns after repeated repository listings, repeated full-suite validation, repeated diffs/status checks, or a configurable command-count milestone. Advice is deduplicated per session and never suppresses a required final full validation.

## Safety

- No command is blocked because of the budget or read cache.
- No model is selected or recommended.
- Checkpoints contain only allow-listed compact facts.
- File changes invalidate read reuse immediately.
- Full outputs and exit codes remain preserved by existing capture behavior.

## Acceptance

- Unit tests prove session reset, unchanged-read recognition, hash invalidation, advice deduplication, command-family thresholds, and checkpoint rendering.
- Hook tests prove advisory Codex envelopes and non-blocking behavior.
- Existing full test suite passes.
- Benchmark acceptance continues to require equivalent repository results and complete validation.
