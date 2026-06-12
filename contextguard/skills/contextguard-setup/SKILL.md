---
name: contextguard-setup
description: Initialize ContextGuard for the current empty or existing project and verify whether Codex lifecycle hooks have actually run. Invoke explicitly with $contextguard-setup.
---

# ContextGuard Setup

Run the bundled command:

```bash
"$PLUGIN_ROOT/scripts/contextguard" setup
```

Report the result directly:

- When `Execution protection: ready` is present, state that host-independent command capture is initialized and ready.
- Report hook status separately. Hooks are optional defense in depth; if they were not observed, mention `/hooks` as an optional enhancement rather than a blocker.
- Do not claim measured savings until commands have been executed through the project runner and appear in `$contextguard-report`.
- Do not edit Codex hook-trust records or bypass the review flow.
