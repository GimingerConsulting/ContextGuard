# Contributing

Keep ContextGuard local-first, dependency-light and safe by default.

- Do not add network calls.
- Do not modify user source code from hooks or CLI maintenance commands.
- Preserve existing user-authored documentation outside managed markers.
- Add tests for command rewriting, path safety and output preservation when changing runtime behavior.
- Run `python3 -m pytest` and plugin validation before submitting changes.
