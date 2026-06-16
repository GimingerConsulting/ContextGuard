# ContextGuard 0.9.0 - Five Additional RAW vs ContextGuard Use Cases

Source run: `.contextguard/reports/final-usecase-ab-2026-06-16/summary.csv` generated from `python3 contextguard/benchmarks/final_usecase_ab.py --run`.

These five cases are intended as an appendix to the existing five-case PDF. They focus on different realistic command-output patterns so the combined document can show ten total RAW vs ContextGuard examples.

## New Use Cases

| # | Segment | Use case | Scenario | RAW visible tokens | ContextGuard visible tokens | Tokens saved | Reduction | Overhead |
|---:|---|---|---|---:|---:|---:|---:|---:|
| 6 | enterprise | database | slow-query-triage | 30,599 | 36 | 30,563 | 99.85% | 62.5 ms |
| 7 | vibecoding | feature-development | map-new-feature-tree | 570 | 50 | 520 | 93.04% | 75.9 ms |
| 8 | smb | testing | billing-test-failure | 909 | 559 | 350 | 46.85% | 221.8 ms |
| 9 | enterprise | testing | e2e-test-failure | 2,009 | 513 | 1,496 | 78.88% | 95.6 ms |
| 10 | enterprise | incident-response | production-log-triage | 28,499 | 73 | 28,426 | 99.70% | 81.1 ms |

## Average For These Five New Cases

- Total RAW visible tokens: 62,586
- Total ContextGuard visible tokens: 1,231
- Total tokens saved: 61,355
- Weighted average reduction: 98.03%
- Mean wrapper overhead: 107.4 ms

## Interpretation

Across these five additional scenarios, ContextGuard reduced visible command-output tokens from RAW by compacting noisy output while preserving the command result for follow-up inspection. The strongest cases are noisy investigation and failure-output workflows; smaller or already-focused commands save less and may mainly provide evidence archiving rather than dramatic token reduction.

## Text To Add To The PDF

Add a second five-case block after the current table:

> In five additional simulated RAW vs ContextGuard use cases, RAW produced 62,586 visible tokens while ContextGuard produced 1,231 visible tokens. That saved 61,355 visible tokens, a weighted average reduction of 98.03%. The cases cover slow-query triage, feature-tree exploration, production-log triage, billing-test failure output, and end-to-end test failure output.

## Notes For The Combined 10-Case Version

- Keep the existing first five PDF cases unchanged.
- Append the five rows above as cases 6-10.
- For the overall 10-case average, add the existing PDF totals to the new-five totals above, then compute `(total_raw - total_contextguard) / total_raw * 100`.
- Label all values as local visible-token estimates from reproducible benchmark output, not verified Codex server-side billing.
