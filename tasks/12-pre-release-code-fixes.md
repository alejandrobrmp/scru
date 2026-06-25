# Task 12: Pre-release Code Fixes

## Goal

Apply four targeted production-readiness fixes to the source code before the v0.1.0 release.

## Scope

- Four code changes across three files (`__init__.py`, `update.py`, `wizard.py`).
- No new dependencies.
- No test changes required (existing tests cover the changed paths adequately).
- No README or spec changes.

## Dependencies

- All prior tasks completed (1 through 11b merged into `develop`).
- No dependency on `tasks/13-changelog-and-linting.md` — these can run in parallel.

## Acceptance Criteria

### Fix 1: `urlopen` timeout (`src/scru/update.py` line 56)

- `urlopen(target_url)` → `urlopen(target_url, timeout=10)` in `resolve_public_source_ipv4`.
- Network hangs from the public IP source are now bounded to 10 seconds.

### Fix 2: `__version__` export (`src/scru/__init__.py`)

- `scru.__version__` returns the version string from `pyproject.toml` via `importlib.metadata.version("scru")`.
- Runtime-accessible, no hardcoded duplication of the version.

### Fix 3: Wizard `_get_zone_name` exception swallowing (`src/scru/wizard.py` lines 347-348)

- When the Cloudflare API call inside `edit()`'s `_get_zone_name` fails, cache `"(API error)"` as the zone display name instead of falling back to the raw zone ID UUID silently.
- Users see a human-readable indicator instead of a confusing UUID.

### Fix 4: `_setup_encoding` silent failure (`src/scru/wizard.py` lines 24-25)

- When `sys.stdout.reconfigure` fails, print a warning to `stderr` instead of silently ignoring.
- Users are informed that box-drawing characters may render incorrectly.

### No regressions

- All 60 existing unit tests continue to pass.
- `ruff check src/` produces zero violations (after ruff config from Task 13).

## Implementation Notes

### Fix 1

```python
# Before (line 56)
with urlopen(target_url) as response:

# After
with urlopen(target_url, timeout=10) as response:
```

`urlopen` from `urllib.request` accepts a `timeout` keyword in seconds. Consistent with the 10s timeout already used for custom source commands via `subprocess.run(timeout=10)`.

### Fix 2

```python
# Before (entire file)
"""SCRU package."""

# After
"""SCRU package."""
from importlib.metadata import version

__version__ = version("scru")
```

`importlib.metadata.version` was added in Python 3.8 and reads from the installed package metadata, so it stays in sync with `pyproject.toml` automatically.

### Fix 3

```python
# Before (line 347-349)
except Exception:
    pass
return zone_cache.get(zid, zid)

# After
except Exception:
    zone_cache[zid] = "(API error)"
return zone_cache.get(zid, zid)
```

By caching `"(API error)"` instead of passing silently, the `dict.get` on the next line returns the human-readable string. Subsequent calls for the same zone_id skip the API and return the cached error indicator.

### Fix 4

```python
# Before (lines 22-25)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# After
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    print("Warning: could not set UTF-8 encoding, display may be garbled", file=sys.stderr)
```

The warning prints to `stderr` so it doesn't interfere with the wizard's stdout-based UI. The wizard continues normally — this is a non-fatal condition.

## Verification

1. Run unit tests:
   ```bash
   pytest tests/ --ignore=tests/integration -v
   ```
   Confirm all 60 tests pass.

2. Quick smoke checks (in a terminal with a Cloudflare token):
   - `python -c "import scru; print(scru.__version__)"` → outputs `0.1.0`.
   - `scru` with a public source record → runs and completes (no hang).
   - `scru config` with a bad token → wizard shows meaningful errors.

3. After Task 13: `ruff check src/` produces zero violations.

## Follow-ups

- Consider adding a `--timeout` CLI flag to let users configure the public source timeout (out of scope for v0.1.0).
- If wizard encoding failure proves common, consider alternative rendering strategies (ASCII-only fallback).
