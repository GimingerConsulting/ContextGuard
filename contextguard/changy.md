# changy.md

## 2026-06-09

### Changes

- Scaffolded `contextguard` as a Codex plugin using the local `plugin-creator` workflow.
- Implemented Python standard-library MVP: project detection, SQLite indexing, managed documentation, command classification, command capture, output compaction, large-file summaries, metrics and CLI.
- Added bundled lifecycle hooks in `hooks/hooks.json`.
- Added explicit Codex skills for init, status, refresh, report and project uninstall.
- Added `agents/openai.yaml` metadata for each skill.
- Added marketplace metadata at `.agents/plugins/marketplace.json`.
- Added repository-root marketplace metadata so `BurliNYC/ContextGuard` can be used as a GitHub marketplace source while the plugin root remains `./contextguard`.
- Added README, contribution, security, changelog, license and benchmark documentation.
- Added tests for project detection, command rewriting, compaction, large files, capsules, documentation safety and hooks.

### Adjustments

- The plugin is under repository path `contextguard/`, matching the requested tree. The repository root is a container for the installable plugin and exposes a root marketplace file that points to `./contextguard`.
- `plugin.json` does not include a top-level `hooks` field because the current local plugin validator rejects unsupported manifest fields. Hooks are present in `hooks/hooks.json` and documented in the README.

### Problems And Solutions

- Problem: the workspace was not initialized as a Git repository.
  Solution: initialize Git before committing and pushing to `BurliNYC/ContextGuard`.

- Problem: PNG assets are required but the MVP does not need custom artwork.
  Solution: include deterministic placeholder PNG assets for validation and later replacement.

- Problem: skill agent YAML initially used flat metadata keys, but current plugin validation requires an `interface` object.
  Solution: updated `agents/openai.yaml` files to the validator-compatible schema.

- Problem: skill agent asset paths must resolve inside the plugin archive from the plugin root.
  Solution: copied placeholder icons into each skill's `assets/` directory and changed skill metadata icons to `assets/icon.png` and `assets/logo.png`, matching validator rules.
