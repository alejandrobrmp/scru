# Task 8: Multi-Record and Multi-Zone Execution

## Goal
Remove the single-record limit and make SCRU process every configured record, including records spread across multiple zones, while keeping failures isolated per record.

## Scope
- Replace the current single-record guard in the run path so `scru` processes all configured records.
- Iterate records in config order and handle each record independently.
- Keep per-record failures from stopping later records.
- Keep the existing source resolution behavior unchanged for fixed, public, and custom sources.
- Keep one-line human-readable output per record result.
- Extend the integration harness so test cases can provision multiple records in one real Cloudflare zone.
- Use suffixed integration env vars for repeated records, for example `*_1`, `*_2`, and so on, so tests can create more than one record without hard-coded plain-text names.
- Add unit tests for multi-record success, skip, and failure isolation.
- Add integration coverage for at least one case with multiple records in one zone.

## Dependencies
- `tasks/07-custom-source-support.md`
- `tasks/05_1-integration-tests.md`
- `tasks/04-one-record-update-slice.md`
- `tasks/03-config-model-and-yaml-io.md`
- `spec/01_spec.md`
- `spec/02_tasks.md`

## Acceptance Criteria
- `scru` no longer fails when the config contains more than one record.
- Every configured record is processed in order.
- A failure in one record does not stop later records.
- Output remains one clear line per record result.
- Fixed, public, and custom source behavior continues to work unchanged inside the per-record loop.
- Unit tests cover multiple records, skip behavior, and failure isolation.
- Integration tests cover a multi-record case in one zone and still clean up copied config files and Cloudflare resources.

## Implementation Notes
- Keep the smallest possible change in the existing run path unless a tiny helper split makes the record loop clearer to test.
- Reuse `src/scru/update.py` as the execution entry point if possible; do not introduce a second run path just for tests.
- Extend `tests/integration/support.py` only as much as needed to support numbered env vars for extra records in the active zone.
- Do not change the YAML config schema for this task.
- Preserve the existing per-record result strings so tests stay easy to read.

## Verification
- Run the targeted unit tests covering multi-record iteration, unchanged-record skips, and isolated failures.
- Run the integration suite with at least one multi-record case in the active zone.
- Confirm the output prints one line per configured record and that later records still run after an earlier failure.

## Follow-ups
- Add a separate wizard task next if config editing needs to support more than one record entry interactively.
- Add more integration permutations later if provider behavior differs across zone states.
