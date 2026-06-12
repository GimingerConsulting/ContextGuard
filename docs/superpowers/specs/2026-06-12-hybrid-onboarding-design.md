# ContextGuard Hybrid Onboarding Design

## Goal

Make ContextGuard usable in empty and existing projects with the smallest safe setup: install the plugin, trust its hooks once in Codex, then let the first `SessionStart` initialize each project automatically.

## Design

- Move project initialization into a reusable, idempotent Python service used by both the CLI and `SessionStart` hook.
- On the first trusted `SessionStart`, initialize `.contextguard/`, the local index, managed documentation sections, and ignore entries. Preserve all user-authored content through the existing managed-section mechanism.
- Record hook heartbeat files under `.contextguard/tmp/` so `status` and the new `setup` command can distinguish package initialization from actual Codex hook execution.
- Add `$contextguard-setup` as the explicit fallback. It initializes the project, reports whether hooks have been observed, and tells the user to open `/hooks` only when trust or dispatch is still missing.
- Keep hook trust as a Codex-controlled user action. ContextGuard must not edit Codex trust records or bypass this security boundary.

## User Flow

1. Install ContextGuard from its marketplace source.
2. Start a new thread in the target project.
3. If Codex requests hook review, open `/hooks`, review the local ContextGuard commands, and trust them once.
4. Start or resume the project thread. ContextGuard initializes the project automatically.
5. Run `$contextguard-setup` at any time for an idempotent setup and diagnostic check.
6. Run `$contextguard-status` or `$contextguard-report` to confirm interception and estimated savings.

## Failure Handling

- Initialization failures must not prevent Codex from starting. `SessionStart` returns a concise fallback message directing the user to `$contextguard-setup`.
- An initialized project without a hook heartbeat is reported as initialized but not yet verified, never as fully protected.
- Upstream Codex surfaces that do not dispatch hooks are reported honestly; no token-savings guarantee is made for those surfaces.

## Validation

- Unit tests cover automatic initialization for empty and existing projects, preservation of user content, idempotency, hook heartbeat diagnostics, and setup output.
- Documentation tests verify the marketplace instructions and the explicit trust boundary.
- The isolated plugin acceptance benchmark verifies the packaged auto-init flow.
- The full test suite and plugin validator must pass before publishing.
