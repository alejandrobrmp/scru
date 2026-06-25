# Task 6: Public Source Support

## Goal
Implement `source.type: public` so SCRU can resolve the machine's current public IPv4 address during record updates.

## Scope
- Add public-source resolution to the existing update/source path.
- Fetch the machine's current public IPv4 from a small, mockable helper.
- Validate the fetched value as exactly one IPv4 address before any Cloudflare read or update call.
- Keep the fixed-source path and config schema unchanged.
- Add focused unit tests for the public-source resolver and update flow.
- Add integration coverage for a public-source end-to-end case using the existing integration harness.

## Dependencies
- `tasks/05-fixed-source-support.md`
- `tasks/05_1-integration-tests.md`
- `tasks/04-one-record-update-slice.md`
- `spec/01_spec.md`
- `spec/02_tasks.md`

## Acceptance Criteria
- A record configured with `source.type: public` resolves to the machine's current public IPv4.
- Invalid, empty, or non-IPv4 public responses fail before any Cloudflare read or update call.
- `process_record` still skips unchanged records and updates changed records for public source input.
- Fixed-source behavior continues to pass unchanged.
- Unit tests cover public-source success and failure paths.
- Integration tests cover at least one public-source end-to-end case and still clean up any copied config or Cloudflare resources.
- The implementation does not require config schema changes.

## Implementation Notes
- Keep the change inside the existing update/source path unless a small helper split makes the network fetch easier to mock.
- Do not hardcode a specific public-IP endpoint into this task spec; choose an implementation that is simple to test and returns plain IPv4 text.
- Reuse `tests/test_update.py` if possible; split tests only if the public-source cases need a separate module to stay readable.
- Extend the existing integration fixtures only as much as needed for the new public-source scenario.

## Verification
- Run the targeted unit tests covering public-source resolution, invalid public responses, unchanged-record skip behavior, and changed-record updates.
- Run the integration suite with the new public-source case and confirm it reports one clear line of output.

## Follow-ups
- Add custom source support next.
- Add more integration coverage if public-source behavior needs additional edge cases later.
