# ContextGuard Benchmark Harness

Run:

```bash
PYTHONPATH=. python3 benchmarks/run_benchmarks.py
```

The harness creates separate baseline and optimized copies for ten scenarios: a trivial change, medium feature, complex failure, verbose test suite, large JSON analysis, repeated errors, long session, unchanged restart, partial-change restart, and large repository.

Each pair uses the same command and starting content. Success requires the same exit code and repository-state hash, excluding ContextGuard's local `.contextguard/` state. The JSON records measured output bytes and duration, estimated token reduction, ContextGuard overhead, and semantic final-response quality.

This is deterministic local tooling, not a complete Codex usage measurement. Token values use a labeled four-bytes-per-token estimate. Real-world claims require controlled Codex A/B runs with the same prompt, model, reasoning level, environment, tools and validation criteria.

## Real Codex Hard A/B

Run the opt-in real model benchmark:

```bash
python3 benchmarks/real_codex_ab.py --self-check
python3 benchmarks/real_codex_ab.py --run
```

The harness creates two identical settlement repositories, uses isolated Codex homes with the same authentication, runs `gpt-5.5` at medium reasoning, parses exact `turn.completed.usage` fields, and validates 130 cases plus canonical CLI output. The optimized copy alone is initialized with ContextGuard and is accepted only when its command event proves use of the project capture runner.

The June 10, 2026 result in `benchmarks/results/real-codex-hard-ab-2026-06-10.json` is retained as a rejected historical hook-dependent sample. The current harness no longer configures or waits for `codex exec` lifecycle hooks; it uses the host-independent runner path and rejects any optimized trial that bypasses it.

## Realistic Production Backend A/B

Run the heavier opt-in benchmark:

```bash
python3 benchmarks/real_codex_backend_ab.py --self-check
python3 benchmarks/real_codex_backend_ab.py --run
```

This harness creates two isolated legacy inventory-service repositories and asks Codex to complete a production-style upgrade involving schema migration, API compatibility, idempotency, optimistic versions, thread-safe reservations, deterministic audit logs, CLI behavior, repository noise, and 329 tests. Acceptance requires both agents to pass every test and produce identical canonical API, migration, and concurrency probe results. The ContextGuard trial must additionally prove project capture-runner use.

## Human Support-Ticket A/B

Run the three-pair human-maintenance benchmark:

```bash
python3 benchmarks/real_codex_support_ab.py --self-check
python3 benchmarks/real_codex_support_ab.py --run
```

Agents receive only an incident ticket, production-style logs, an unfamiliar legacy service and three public tests. A separate hidden suite checks 144 observable customer requirements after the agent finishes. Three pairs run in counterbalanced order, and every individual trial uses a separate temporary root so agents cannot inspect the comparison repository. This benchmark measures realistic diagnosis behavior, where model exploration choices can dominate total tokens and time.

## Human CI-Investigation A/B

Run:

```bash
python3 benchmarks/real_codex_ci_ab.py --self-check
python3 benchmarks/real_codex_ci_ab.py --run
```

This benchmark starts with a locally green reporting service, a PR review note, and a large CI failure artifact covering timezone and DST cases. Agents must diagnose the discrepancy, add regression tests, preserve the public API, and update the changelog. Two counterbalanced pairs use separate temporary roots; acceptance requires all 160 hidden CI cases and the canonical CLI result.

## Host-Independent Capture A/B

Run:

```bash
python3 benchmarks/host_capture_ab.py --self-check
python3 benchmarks/host_capture_ab.py --run
```

This benchmark does not use ContextGuard hooks. Both Codex trials receive the same prompt and deterministic 130-failure command. The raw project runs the command directly; the initialized project must follow managed `AGENTS.md` instructions and execute it through `.contextguard/bin/contextguard capture`. The result is rejected unless both trials issue one command, produce the same exact final response, and the optimized command event proves runner usage.

The accepted June 12, 2026 run measured 34,008 raw versus 22,673 ContextGuard input tokens, 14,808 versus 9,617 uncached input tokens, 38,490 versus 1,899 tool-output bytes, and 9.701 versus 6.944 seconds. This is one controlled real Codex sample, not a universal guarantee.

## Direct Output A/B

Run `python3 benchmarks/output_ab.py` to compare the exact same hard 130-failure pytest output as fully visible RAW output and as the real ContextGuard PostToolUse response. The test counts visible bytes and `o200k_base` tokens, measures median processing time, verifies that the complete archived output is byte-identical, and requires the compact response to retain the test summary and concrete failed-test names.

The June 10 result in `benchmarks/results/output-ab-2026-06-10.json` measured 20,650 RAW tokens versus 543 ContextGuard tokens, saving 20,107 tokens or 97.37%, with 42.5 ms median additional processing time across eleven samples.

## Isolated Installation Acceptance

Run `python3 benchmarks/install_acceptance.py` to copy the publishable plugin into an isolated installation directory and test only that copy. Acceptance requires successful one-time initialization of both an empty project and an existing Git project, preservation of user-authored instructions, successful SessionStart/UserPromptSubmit/PreToolUse/PostToolUse processing, byte-identical archived raw output, retained failure information, and positive visible-token savings.

The June 10 acceptance result in `benchmarks/results/install-acceptance-2026-06-10.json` passed every gate. The hard 130-failure output used 14,581 RAW tokens versus 528 ContextGuard-visible tokens, saving 14,053 tokens or 96.38%. This deterministically guarantees the packaged ContextGuard logic under the simulated hook lifecycle; it does not guarantee that an external Codex host version dispatches hooks or that a stochastic model returns identical prose or code.

The June 12 acceptance additionally begins with uninitialized empty and existing projects and requires the packaged `SessionStart` hook to initialize both automatically while preserving existing instructions. Its result is stored in `benchmarks/results/install-acceptance-2026-06-12.json`.
