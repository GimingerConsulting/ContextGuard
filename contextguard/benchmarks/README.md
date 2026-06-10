# ContextGuard Benchmark Harness

Run:

```bash
PYTHONPATH=. python3 benchmarks/run_benchmarks.py
```

The harness creates separate baseline and optimized copies for ten scenarios: a trivial change, medium feature, complex failure, verbose test suite, large JSON analysis, repeated errors, long session, unchanged restart, partial-change restart, and large repository.

Each pair uses the same command and starting content. Success requires the same exit code and repository-state hash, excluding ContextGuard's local `.contextguard/` state. The JSON records measured output bytes and duration, estimated token reduction, ContextGuard overhead, and semantic final-response quality.

This is deterministic local tooling, not a complete Codex usage measurement. Token values use a labeled four-bytes-per-token estimate. Real-world claims require controlled Codex A/B runs with the same prompt, model, reasoning level, environment, tools and validation criteria.
