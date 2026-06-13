# Changelog

## 0.4.0

- Added versioned, allow-listed session checkpoints for compact resume context.
- Added session-scoped SHA-256 tracking for exact repeated `cat` and `sed -n` reads, with immediate invalidation when a file changes.
- Added a non-blocking command budget for repeated repository listings, repository checks, excessive full-suite validation, and long command sequences.
- Added status metrics for tracked commands, repeated reads, and emitted budget advice.
- Kept model selection entirely user-controlled and preserved all commands, validation, exit codes, and archived output.

## 0.3.2

- Made every lifecycle hook fail open when a running thread references a plugin cache directory removed by an update or uninstall.
- Added regression coverage for stale cached hook commands so missing plugin files cannot block prompts, tools, compaction or thread completion.

## 0.3.1

- Fixed wheel and editable installation by restricting setuptools discovery to the `contextguard` package.
- Declared and validated Python 3.9 as the minimum runtime used by Codex plugin hooks and scripts.
- Removed the real Codex A/B harness dependency on `codex exec` lifecycle-hook dispatch; optimized trials now require the host-independent project capture runner.
- Added packaging, Python-minimum and non-interactive runner regression coverage.

## 0.3.0

- Added the executable project-local `.contextguard/bin/contextguard` runner.
- Changed managed project instructions to route noisy commands through `capture` before stdout reaches Codex.
- Made output protection independent of lifecycle hook dispatch and output replacement behavior.
- Added truthful runner readiness reporting, isolated installed-runner acceptance and a real Codex host A/B benchmark.
- Measured the accepted host A/B at 33.33% fewer input tokens, 35.06% fewer uncached input tokens, 95.07% less tool output and 28.42% lower elapsed time for the same validated result.

## Unreleased

- Added the Adaptive Maximum Efficiency output policy and final-response quality checks.
- Added structured unique errors, warnings, failed tests, stack traces and complete local output retention.
- Added compact session-resume capsules, cache-reuse metrics and bounded policy overhead reporting.
- Reworked benchmarks around equivalent exit codes and repository-state hashes across ten scenarios.

## 0.1.0

- Initial MVP with local project initialization, SQLite indexing, managed documentation, command capture, large-output compaction, lifecycle hooks, explicit skills, tests and marketplace metadata.
