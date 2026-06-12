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

- When a tool hook was observed, state that ContextGuard is initialized and ready.
- When only `SessionStart` was observed, state that setup is partial and ask Codex to run one normal tool command before checking `$contextguard-status`.
- When hooks were not observed, tell the user to open `/hooks`, review and trust the ContextGuard hooks, and then start a new thread in the project.
- Do not claim token savings until hooks have been observed and commands have been intercepted.
- Do not edit Codex hook-trust records or bypass the review flow.
