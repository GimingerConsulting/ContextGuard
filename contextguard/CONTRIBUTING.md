# Contributing

Keep ContextGuard local-first, dependency-light and safe by default.

## Licensing

By submitting a contribution to this repository, you agree that your contribution may be used under the project's current licensing structure, including the [PolyForm Noncommercial License 1.0.0](../LICENSE) for noncommercial use and separate commercial licensing terms where applicable.

Giminger Consulting may require an additional contributor agreement before accepting external contributions. Repository owners should review contribution licensing with counsel before merging substantial third-party work.

- Do not add network calls.
- Do not modify user source code from hooks or CLI maintenance commands.
- Preserve existing user-authored documentation outside managed markers.
- Add tests for command rewriting, path safety and output preservation when changing runtime behavior.
- Run `python3 -m pytest` and plugin validation before submitting changes.
