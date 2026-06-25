# Task 9: Cloudflare Update Rules

## Goal

Make SCRU respect Cloudflare update rules for `proxied` and `ttl`, so unchanged records are skipped correctly and provider-enforced TTL values are not fought.

## Scope

- Extend the skip check in `src/scru/update.py` so a record is only skipped when `content`, `proxied`, and `ttl` all match the current Cloudflare state.
- Normalize the provider-enforced `ttl: 1` (auto) value for proxied records during the skip comparison, so SCRU does not loop on a "always different" ttl.
- When a record has `proxied: true` and a configured `ttl`, emit one warning line and omit `ttl` from the PATCH so Cloudflare applies auto TTL.
- Keep `proxied` and `ttl` handling for non-proxied records unchanged.
- Keep the existing per-record failure isolation and one-line-per-record output behavior.
- Add unit tests in `tests/test_update.py` covering the new skip and ttl-normalization behavior.
- Do not change the YAML config schema.
- Do not introduce new modules.

## Dependencies

- `tasks/08-multi-record-and-multi-zone-execution.md`
- `tasks/07-custom-source-support.md`
- `tasks/04-one-record-update-slice.md`
- `tasks/03-config-model-and-yaml-io.md`
- `spec/01_spec.md`
- `spec/02_tasks.md`

## Acceptance Criteria

- A record whose `content` matches but `proxied` differs is updated, not skipped.
- A record whose `content` matches but `ttl` differs (non-proxied case) is updated, not skipped.
- A record whose `content`, `proxied`, and `ttl` all match is skipped with the existing `skipped (unchanged)` line.
- A proxied record whose Cloudflare state returns `ttl: 1` (auto) and whose config has no `ttl` is skipped, not updated in a loop.
- A record configured with `proxied: true` and a `ttl` value prints one warning line explaining the ttl will be ignored, and the PATCH sent to Cloudflare omits `ttl`.
- A record configured with `proxied: true` and no `ttl` behaves as today (no warning, no `ttl` in PATCH).
- Non-proxied records continue to send the configured `ttl` unchanged.
- All existing unit tests continue to pass.
- New unit tests cover: skip on full match, update when only `proxied` differs, update when only `ttl` differs, skip for proxied record with `ttl: 1` returned and no config ttl, and the proxied+ttl warning path with ttl omitted from the PATCH.

## Implementation Notes

- Keep the change localized to `process_record` in `src/scru/update.py`; do not split the run path.
- Compare `proxied` and `ttl` against `current.get("proxied")` and `current.get("ttl")` from the Cloudflare response.
- For the skip comparison only, treat `ttl: 1` from Cloudflare as equivalent to "no user ttl" when `record.proxied is True` and `record.ttl is None`.
- Emit the proxied+ttl warning via the `output` callable passed into `main`, not via direct `print`, so tests can capture it. This means `process_record` needs a way to surface the warning; prefer returning a structured signal or passing `output` into `process_record` rather than introducing a second side channel. Keep the change minimal.
- Do not validate or reject the config at load time for the proxied+ttl combination; the warning is emitted at run time only.
- Preserve the existing result strings (`updated`, `skipped (unchanged)`, `failed (...)`).
- The warning line format should be: `<name>: warning (ttl ignored for proxied record)`, printed before the final result line.
- Do not change `src/scru/cloudflare.py` for this task.
- Do not change `src/scru/config.py` for this task.

## Verification

- Run `pytest tests/test_update.py` and confirm all new and existing cases pass.
- Run the full unit test suite (`pytest`) and confirm no regressions.
- Run the real app once with a config containing one proxied record plus a configured ttl and confirm:
  - One warning line is printed.
  - The record is updated (or skipped if content already matches).
  - No second update happens on a re-run when content matches.

## Follow-ups

- Add integration coverage for proxied records with provider-enforced ttl if provider behavior needs end-to-end confirmation.
- Consider wizard-side guidance (task 10) to warn the user interactively when they configure proxied + ttl.
