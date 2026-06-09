# changy.md

See [contextguard/changy.md](contextguard/changy.md) for the detailed implementation protocol.

## 2026-06-09

- Built the initial ContextGuard Codex plugin MVP under `contextguard/`.
- Added repository-root marketplace metadata for GitHub source installation.
- Verified tests with `python3 -m pytest`: 19 passed.
- Verified plugin schema with `plugin-creator/scripts/validate_plugin.py`: passed.

## 2026-06-09 Readiness Pass

- Strengthened ContextGuard internals for real use before manual testing.
- Expanded tests to 29 cases.
- Added benchmark harness and richer metrics.

## 2026-06-09 Savings Improvements

- Added medium noisy-output compaction and shorter high-confidence capsules.
- Added visible lifetime savings estimates in status/report.
- Expanded tests to 34 cases.
- Realistic A/B improved to 81.64% estimated token savings with identical patch and passing tests.

## 2026-06-09 Marketplace Presentation

- Updated marketplace-facing plugin metadata and visuals.
- Corrected developer name to Giminger Consulting.
- Added branded PNG icon, logo and screenshot assets.

## 2026-06-09 Marketplace Manifest Alignment

- Aligned `plugin.json` interface metadata with the new ContextGuard marketplace copy.
- Removed screenshot metadata so the plugin page relies on `icon.png` and `logo.png`.
- Changed plugin category metadata to `Productivity`.

## 2026-06-09 Complex Context Savings Test

- Re-validated the plugin manifest and full test suite: 34 passed.
- Ran the built-in benchmark harness across 7 fixtures.
- Ran a complex RAW-vs-ContextGuard feature simulation for temporary billing price override windows.
- Result: both workflows passed the same 6 feature tests with identical invoice output.
- Measured estimate: RAW 219,896 tokens vs ContextGuard 3,138 tokens, saving 216,758 tokens or 98.57%.

## 2026-06-09 Harder Time And Token Test

- Ran a harder RAW-vs-ContextGuard simulation for risk-aware order fulfillment with holds, partial inventory allocation, fraud signals, shipping-zone blocks, surcharges and audit trails.
- Result: both workflows passed the same 31 tests and produced identical sample fulfillment output.
- Measured estimate: RAW 664,211 tokens vs ContextGuard 4,417 tokens, saving 659,794 tokens or 99.34%.
- Local harness time: RAW 0.7779s, ContextGuard 1.5808s, meaning ContextGuard was slower locally because of init/capture overhead.
- Projected model-processing time at 3,000 tokens/s: RAW 222.1815s total vs ContextGuard 3.0532s total, a projected 98.63% time reduction.

## 2026-06-09 Hardest Returns Benchmark

- Ran a harder valid RAW-vs-ContextGuard simulation for resilient returns and refund orchestration.
- Result: both workflows passed the same 53 tests and produced identical sample return output.
- Measured estimate: RAW 1,319,139 tokens vs ContextGuard 4,263 tokens, saving 1,314,876 tokens or 99.68%.
- Local harness time: RAW 0.8120s, ContextGuard 1.5270s, meaning ContextGuard was slower locally because of init/capture overhead.
- Projected model-processing time at 3,000 tokens/s: RAW 440.5250s total vs ContextGuard 2.9480s total, a projected 99.33% time reduction.
