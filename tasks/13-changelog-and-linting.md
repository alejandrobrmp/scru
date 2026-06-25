# Task 13: Changelog and Linting Configuration

## Goal

Add a `CHANGELOG.md` for the v0.1.0 release and a minimal `ruff` configuration to `pyproject.toml` for ongoing code quality.

## Scope

- New file: `CHANGELOG.md` at repo root with v0.1.0 release notes.
- Modified file: `pyproject.toml` — add `[tool.ruff]` and `[tool.ruff.lint]` sections.
- No code changes.
- No new dependencies (ruff is a dev tool, not a runtime dependency).

## Dependencies

- All prior tasks completed (1 through 11b merged into `develop`).
- No dependency on `tasks/12-pre-release-code-fixes.md` — these can run in parallel.

## Acceptance Criteria

### CHANGELOG.md

- File exists at repo root.
- Contains a `## 0.1.0` entry with the current date.
- Lists all features present in the first release, grouped by category (DNS Updates, Configuration, CLI, CI/CD).
- Follows [Keep a Changelog](https://keepachangelog.com/) conventions (Unreleased → versioned sections).

### Ruff config

- Added to `pyproject.toml` under `[tool.ruff]` and `[tool.ruff.lint]`.
- Targets Python 3.11.
- Enables these rule sets:
  - `E`, `F` — pycodestyle errors + pyflakes (basic correctness).
  - `I` — isort-compatible import ordering.
  - `UP` — pyupgrade (modern syntax for 3.11+).
  - `B` — flake8-bugbear (common bug patterns).
  - `SIM` — flake8-simplify (unnecessary complexity).
  - `C4` — flake8-comprehensions (idiomatic comprehensions).
- After Task 12 fixes are applied, `ruff check src/` produces zero violations.

## Implementation Notes

### CHANGELOG.md structure

```markdown
# Changelog

## 0.1.0 — 2026-06-25

### Added

- **DNS Update Engine**: update Cloudflare A records from IPv4 sources.
- **Fixed, Public (ipify), and Custom command** IP source types.
- **Multi-record and multi-zone** execution with per-record failure isolation.
- **Cloudflare update rules**: proxied/TTL normalization, skip-on-unchanged, proxied+TTL warning.
- **Interactive config wizard** (`scru config`) with new/edit modes, zone/record browsing, and back navigation.
- **CLI** with `scru` (run updates) and `scru config` (wizard) commands.
- **YAML config** at `~/.config/scru/config.yaml`.
- **CI/CD**: PR validation (unit + integration tests), release branch builds, main-merge releases.
- **README** with full user documentation.
```

Group features logically, keep it concise.

### Ruff config

```toml
[tool.ruff]
target-version = "py311"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "C4"]
```

No formatter config — only linting. Keeps it minimal and non-intrusive. The rule set catches real bugs (E/F/B) and enforces modern idioms (UP/SIM/C4/I) without noisy whitespace warnings.

## Verification

1. Confirm `CHANGELOG.md` exists and the date/version are correct.
2. Run `ruff check src/` — expect zero errors after Task 12 fixes are applied.
3. Run `ruff check tests/` — expect zero errors.
4. Run `git diff --stat` — only `pyproject.toml` modified, `CHANGELOG.md` added.

## Follow-ups

- Update `CHANGELOG.md` on every future release with the new version section.
- Consider adding `[tool.ruff.format]` for auto-formatting in a future task.
- Consider adding `[tool.ruff.lint.isort]` for finer-grained import ordering control.
