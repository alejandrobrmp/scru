# Task 5: Fixed Source Support

## Goal
Implement fixed IPv4 source resolution for record updates.

## Scope
- Support `source.type: fixed` using the configured IPv4 string.
- Validate the fixed source value as a real IPv4 address before any Cloudflare update call.
- Keep the one-record update flow from task 4 unchanged except for using the real fixed source resolver.
- Reject unsupported source types in this task with a clear error.

## Dependencies
- `tasks/04-one-record-update-slice.md`
- `tasks/03-config-model-and-yaml-io.md`
- `tasks/02-pr-unit-test-workflow.md`
- `tasks/01-cli-skeleton.md`
- `spec/01_spec.md`
- `spec/02_tasks.md`

## Acceptance Criteria
- A record configured with `source.type: fixed` resolves to the configured IPv4 address.
- Invalid fixed source values fail before any Cloudflare read or update call.
- `process_record` still skips unchanged records and updates changed records using the resolved fixed IPv4.
- Unsupported source types fail with a short, clear error.
- The change is covered by focused unit tests.

## Implementation Notes
- Keep the change in the existing update/source path; do not start public or custom source support yet.
- Use Python's standard `ipaddress` module for IPv4 validation instead of a custom parser.
- `src/scru/update.py` already owns the source resolver hook from task 4, so fill that in rather than adding a parallel flow.
- Keep the current `tests/test_update.py` coverage style unless a split is strictly necessary.

## Verification
- Add or update focused tests for:
  - valid fixed IPv4 source resolution
  - invalid fixed IPv4 rejection
  - unchanged record still skips
  - changed record still updates
- Run the targeted update tests.

## Follow-ups
- Add public source support.
- Add custom source support.
- Expand from one record to all configured records.
