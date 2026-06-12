# Changelog

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
