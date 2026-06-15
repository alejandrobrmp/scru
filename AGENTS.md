# Project Instructions

## Product Rules

- Keep SCRU lightweight, simple, and understandable.
- Preserve the frozen spec in `spec/01_spec.md`.
- Treat `master` as protected production branch.
- Treat `develop` as the integration branch.
- Start task branches from `develop` and merge changes back via PRs.
- Use `X.X.X` release tags from `master`.

## Workflow Rules

- Do not plan for direct pushes or commits to `master`.
- Do not use `develop` for routine direct pushes or commits.
- If the user explicitly asks to work on the current branch or directly on `develop`, treat that as a scoped exception for that session.
- PRs should run unit tests.
- Releases should build from tagged `master` commits.

## Implementation Rules

- Keep changes minimal.
- Prefer clarity over abstraction.
- Avoid adding complexity not called for by the spec.
