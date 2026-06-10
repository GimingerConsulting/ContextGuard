# ContextGuard

ContextGuard helps Codex produce the same correct result with less wasted input, less unnecessary output and faster task completion.

Developer: Giminger Consulting

It optimizes repository input context, repeated session context, terminal and test output, large structured data, model-generated explanations, final responses, and repeated code or diff output. It automatically expands context when correctness requires it.

## What It Does

ContextGuard is a local-first Codex plugin with explicit skills, lifecycle hooks and deterministic Python tooling. It indexes repository metadata locally, writes compact project guidance, captures large command output to disk, summarizes large data files, and injects small task capsules when there is enough evidence to help Codex start with targeted inspection.

It uses one policy: **Adaptive Maximum Efficiency**. The policy starts with metadata, symbol locations and focused ranges, reuses verified unchanged facts, and escalates through complete symbols, dependencies, files and wider repository context whenever evidence is insufficient.

The output-efficiency engine suppresses routine narration, request restatement, source echo, full diffs and unrelated closing suggestions by default. Completed-task responses retain changed files, validation results and any real blocker, limitation or unverified assumption. Explicit requests for detailed explanations still take precedence.

## Privacy

ContextGuard sends no repository content or telemetry to external services. It uses Python 3 standard library modules and SQLite. Local state is stored under `.contextguard/` inside the project.

## Install From GitHub Marketplace Source

Add the marketplace source:

```bash
codex plugin marketplace add BurliNYC/ContextGuard
```

In the Codex app:

```text
Plugins -> Add More -> Add Source -> GitHub
```

After adding the source, install `contextguard` from the ContextGuard marketplace. Review the bundled hooks before trusting them. They are local Python scripts under `hooks/` and do not use a network API.

To update the marketplace, refresh the source in Codex. To update the plugin, pull the repository or update the marketplace source, then reinstall or refresh the plugin in Codex. To disable the plugin, disable it in Codex plugin settings. To remove the marketplace, remove the `BurliNYC/ContextGuard` source from Codex.

## Project Initialization

Run once in a project:

```bash
contextguard init
```

or invoke `$contextguard-init` in Codex.

Initialization creates `.contextguard/`, a local SQLite index, managed sections in `AGENTS.md`, `docs/ARCHITECTURE.md`, and `docs/CURRENT_STATE.md`, and backups before replacing existing managed sections. It never blindly overwrites user-authored content.

## Daily Commands

```bash
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
- Hooks provide normal runtime behavior with compact context and output protection.
- The Python package performs project detection, indexing, documentation updates, command classification, output capture, large-file summaries and local metrics.
- SQLite stores metadata, hashes, symbols, command executions, cache reuse and conservative savings estimates.

## Quality Guard

ContextGuard never blocks legitimate inspection or skips relevant validation to preserve a token estimate. It does not hide failures, warnings, security concerns or data-integrity risks. Complete command output, stderr, exit code and duration are stored under `.contextguard/tmp/`; Codex receives unique errors, warnings, failed tests and paths for targeted follow-up inspection.

## Supported Platforms

macOS is the primary target. Linux is supported where Python 3 and shell semantics are compatible. `ripgrep` is used when available in future retrieval paths; the MVP keeps a Python fallback.

## Known Hook Limitations

Codex hook support varies by surface and CLI version. ContextGuard uses the current nested `hooks/hooks.json` schema and PostToolUse replacement feedback as a fallback when older CLIs execute hooks but do not apply PreToolUse input rewriting. As of Codex CLI 0.139.0, `codex exec` has an upstream regression that can skip lifecycle hooks entirely even with trust bypass enabled; ContextGuard cannot reduce model-visible command output in that surface until Codex dispatches the hooks. Complete output remains stored locally when hooks run.

## Benchmarks

Use `benchmarks/run_benchmarks.py` to compare baseline and optimized runs from equivalent starting states. A scenario succeeds only when exit codes and repository-state hashes match. Output bytes and duration are measured; token reduction is estimated and labeled as such. The harness does not claim universal savings or exact Codex server-side usage.

## Uninstall

Run:

```bash
contextguard uninstall-project
contextguard uninstall-project --yes
```

The first command explains project-local files. The second removes `.contextguard` state. Managed Markdown sections and user content are preserved unless you remove them manually.

## Roadmap

- Richer cross-language caller extraction.
- Real Codex A/B runs with server-reported token usage where available.
- More hook-surface compatibility tests.

## Disclaimer

Token values in reports are conservative estimates. ContextGuard does not claim exact Codex server-side usage reduction.
