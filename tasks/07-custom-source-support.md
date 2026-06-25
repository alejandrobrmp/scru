# Task 7: Custom Source Support

## Goal
Implement `source.type: custom` so SCRU can run a configured command, such as `tailscale ip --4`, and use its exact stdout as the record IPv4.

## Scope
- Add custom-source resolution to the existing update/source path.
- Run the configured `source.command` as an external command.
- Use the command's exact stdout as the source IPv4 after trimming surrounding whitespace.
- Validate the resolved value as exactly one IPv4 address before any Cloudflare read or update call.
- Enforce a 10-second timeout for the command.
- Keep fixed and public source behavior unchanged.
- Add focused unit tests for custom-source success and failure paths.
- Add one integration case that exercises custom source end to end with a local command stub that behaves like `tailscale ip --4`.

## Dependencies
- `tasks/06-public-source-support.md`
- `tasks/05_1-integration-tests.md`
- `tasks/04-one-record-update-slice.md`
- `tasks/03-config-model-and-yaml-io.md`
- `spec/01_spec.md`
- `spec/02_tasks.md`

## Acceptance Criteria
- A record configured with `source.type: custom` resolves from the configured command output.
- A command like `tailscale ip --4` can be used as the custom source command.
- The command output must be exactly one valid IPv4 string after trimming whitespace.
- Empty output, multiple lines, nonzero exit, or timeout fail before any Cloudflare read or update call.
- The timeout is 10 seconds.
- `process_record` still skips unchanged records and updates changed records for custom source input.
- Fixed-source and public-source behavior continue to pass unchanged.
- Unit tests cover custom-source success and failure paths.
- Integration tests cover at least one custom-source end-to-end case and still clean up any copied config or Cloudflare resources.
- The implementation does not require config schema changes.

## Implementation Notes
- Keep the change inside the existing update/source path unless a small helper split makes command execution easier to test.
- Prefer the standard library for command execution and timeout handling.
- Treat the command as user-provided input from config; do not add shell-specific parsing beyond what is needed to run the configured command safely.
- Reuse `tests/test_update.py` if possible; split tests only if the custom-source cases need a separate module to stay readable.
- Add a dedicated unit test file if needed for command execution and stdout validation.
- Extend the existing integration fixtures only as much as needed for the new custom-source scenario.

## Verification
- Run targeted unit tests covering custom-source resolution, invalid command output, timeout handling, unchanged-record skip behavior, and changed-record updates.
- Run the integration suite with the new custom-source case and confirm it reports one clear line of output.

## Follow-ups
- Add more custom-source edge cases later if command execution behavior needs additional coverage.
- Add any future source types in their own task instead of expanding this one.
