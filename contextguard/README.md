# ContextGuard

ContextGuard helps Codex produce the same correct result with less wasted input, less unnecessary output and faster task completion.

Developer: Giminger Consulting

It optimizes repository input context, repeated session context, terminal and test output, large structured data, model-generated explanations, final responses, and repeated code or diff output. It automatically expands context when correctness requires it.

## What It Does

ContextGuard is a local-first Codex plugin with explicit skills, a project-local capture runner, optional lifecycle hooks and deterministic Python tooling. It indexes repository metadata locally, writes compact project guidance, captures large command output before it reaches Codex, summarizes large data files, and injects small task capsules when there is enough evidence to help Codex start with targeted inspection.

It uses one policy: **Adaptive Maximum Efficiency**. The policy starts with metadata, symbol locations and focused ranges, reuses verified unchanged facts, and escalates through complete symbols, dependencies, files and wider repository context whenever evidence is insufficient.

The output-efficiency engine suppresses routine narration, request restatement, source echo, full diffs and unrelated closing suggestions by default. Completed-task responses retain changed files, validation results and any real blocker, limitation or unverified assumption. Explicit requests for detailed explanations still take precedence.

## Privacy

ContextGuard sends no repository content or telemetry to external services. It supports Python 3.9 and newer and uses standard-library modules plus SQLite. Local state is stored under `.contextguard/` inside the project.

## Fast Setup From The Codex Marketplace

ContextGuard supports empty projects and existing repositories. It preserves user-authored content and only replaces sections marked as ContextGuard-managed.

1. Add the GitHub marketplace source:


```bash
codex plugin marketplace add BurliNYC/ContextGuard
```

   In the Codex app, the equivalent path is:

```text
Plugins -> Add More -> Add Source -> GitHub
```

2. Install `contextguard` from the ContextGuard marketplace and start a new thread in the project you want to use.

3. Run `$contextguard-setup`. It initializes the project and creates `.contextguard/bin/contextguard`, which protects noisy command output without depending on hooks.

4. Optional: when Codex reports that hooks need review, open `/hooks` and trust the local ContextGuard hooks for automatic session initialization and extra protection on supported surfaces.

5. Start a new thread after initial setup so Codex loads the managed `AGENTS.md` capture policy.

## Smoke Test

Run `$contextguard-setup`, then ask Codex to execute a command that produces substantial repeated output. Afterwards run `$contextguard-status` and `$contextguard-report`.

A successful smoke test shows:

- `Project: initialized`
- `Execution protection: ready`
- a project runner under `.contextguard/bin/contextguard`
- at least one intercepted command after tool use
- full large output archived under `.contextguard/tmp/` when compaction was needed

Hook observations are reported separately. Missing hooks do not disable project-runner protection. Trusting hooks remains optional and ContextGuard never edits hook-trust records.

To update the marketplace, refresh the source in Codex. To update the plugin, pull the repository or update the marketplace source, then reinstall or refresh the plugin in Codex. To disable the plugin, disable it in Codex plugin settings. To remove the marketplace, remove the `BurliNYC/ContextGuard` source from Codex.

## Project Initialization

Normal initialization is automatic on the first trusted `SessionStart`. The explicit alternatives are:

```bash
contextguard setup
contextguard init
```

or invoke `$contextguard-setup` or `$contextguard-init` in Codex. Prefer setup because it also checks whether hooks have been observed.

Initialization creates `.contextguard/`, the executable `.contextguard/bin/contextguard` runner, a local SQLite index, managed sections in `AGENTS.md`, `docs/ARCHITECTURE.md`, and `docs/CURRENT_STATE.md`, and backups before replacing existing managed sections. It never blindly overwrites user-authored content.

## Daily Commands

```bash
contextguard setup
contextguard status
contextguard refresh
contextguard report
contextguard capture -- pytest -q
contextguard large-file data.json --contains error --limit 10
contextguard uninstall-project
```

`status` and `report` show measured raw and compact output bytes, managed-policy and capsule overhead, cache reuse, and estimated token reduction. Token values are local estimates, not exact Codex server-side usage numbers.

## Architecture

- Skills provide explicit user commands.
- The project-local runner compacts noisy command output before the host receives stdout.
- Hooks provide optional automatic initialization and defense in depth.
- The Python package performs project detection, indexing, documentation updates, command classification, output capture, large-file summaries and local metrics.
- SQLite stores metadata, hashes, symbols, command executions, cache reuse and conservative savings estimates.

## Quality Guard

ContextGuard never blocks legitimate inspection or skips relevant validation to preserve a token estimate. It does not hide failures, warnings, security concerns or data-integrity risks. Complete command output, stderr, exit code and duration are stored under `.contextguard/tmp/`; Codex receives unique errors, warnings, failed tests and paths for targeted follow-up inspection.

## Supported Platforms

macOS is the primary target. Linux is supported where Python 3 and shell semantics are compatible. `ripgrep` is used when available in future retrieval paths; the MVP keeps a Python fallback.

## Hook Compatibility

Codex hook support varies by surface and CLI version. ContextGuard does not depend on hook dispatch, command rewriting or output replacement: managed project instructions execute noisy commands through the local runner before stdout reaches Codex, including non-interactive runs. Hooks use the current nested schema and remain useful for automatic setup and fallback compaction where supported.

Hook commands are enabled by default in Codex but non-managed hooks require one explicit review in `/hooks`. This trust decision cannot and should not be automated by the plugin. ContextGuard automates project setup immediately after Codex dispatches the trusted `SessionStart` hook.

## Benchmarks

Use `benchmarks/run_benchmarks.py` for deterministic local scenarios and `benchmarks/host_capture_ab.py --run` for a controlled real Codex A/B. The June 12 accepted host run used the same prompt and result in both trials, observed the raw command in baseline and the project runner in ContextGuard, and measured 34,008 versus 22,673 input tokens, 14,808 versus 9,617 uncached input tokens, 38,490 versus 1,899 tool-output bytes, and 9.701 versus 6.944 seconds. This is one controlled sample, not a universal savings guarantee.

## Uninstall

Run:

```bash
contextguard uninstall-project
contextguard uninstall-project --yes
```

The first command explains project-local files. The second removes `.contextguard` state. Managed Markdown sections and user content are preserved unless you remove them manually.

## Roadmap

- Richer cross-language caller extraction.
- Broader repeated real Codex A/B samples across task types and host versions.
- More hook-surface compatibility tests.

## Disclaimer

Local report token values are estimates. Real A/B result files use exact Codex `turn.completed.usage` values and remain scoped to their controlled samples.
