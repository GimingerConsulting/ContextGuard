# Host-Independent Capture Design

## Objective

Make ContextGuard reduce model-visible command output even when Codex ignores `PreToolUse.updatedInput`, does not dispatch hooks, or preserves the original `PostToolUse` result.

## Architecture

Initialization creates an executable project-local runner at `.contextguard/bin/contextguard`. The runner imports the installed ContextGuard package from its actual plugin directory and exposes the existing CLI. Managed `AGENTS.md` instructions require Codex to prepend this runner to commands that can emit large output. Compaction therefore happens inside the command process before stdout reaches the host.

Hooks remain enabled as defense in depth for hosts that support them, but setup readiness and savings claims no longer depend on hooks. Status reports project runner readiness and hook observations separately.

## Command Policy

Use `.contextguard/bin/contextguard capture -- <command> <args...>` for full tests, linters, builds, recursive listings or searches, verbose Git output, logs, structured datasets and commands expected to exceed roughly 4 KB. Use `capture -- sh -lc '<command>'` only when shell syntax is required. Small scoped reads and commands remain direct to avoid overhead.

The wrapper preserves the child exit code, archives stdout and stderr separately, and prints either the unchanged small output or a compact failure/status summary with local artifact paths.

## Verification

Deterministic acceptance must prove that the generated runner works from an isolated installed plugin copy, preserves non-zero exit codes and equivalent result information, and materially reduces visible output. A real Codex A/B benchmark must use the same prompt and fixture, reject optimized runs that do not execute the runner, validate identical behavior, and report exact `turn.completed.usage` fields without universal claims.

## Packaging

Release as `0.3.0`. Setup and refresh regenerate the runner so updating the plugin and rerunning setup moves projects to the current installed implementation.
