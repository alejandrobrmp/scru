# Task 4: One-Record Update Slice

## Goal
Implement the record update flow for one configured `A` record.

## Scope
- Read the existing config model from task 3.
- Process exactly one record at a time.
- Resolve the record source IPv4.
- Fetch the current Cloudflare record state.
- Skip the update when the value is unchanged.
- Update the record when the value changed.
- Print one clear line for success, skip, or failure.
- Keep failures isolated to the single record being processed.

## Dependencies
- `tasks/03-config-model-and-yaml-io.md`
- `tasks/02-pr-unit-test-workflow.md`
- `tasks/01-cli-skeleton.md`
- `spec/01_spec.md`
- `spec/02_tasks.md`

## Acceptance Criteria
- A single configured `A` record can be processed end to end.
- The source IPv4 is resolved before any Cloudflare update call.
- If the current record already matches the source IPv4, the record is skipped.
- If the value differs, the record is updated.
- A single-line human-readable result is printed for the record.
- A failure in this flow does not crash the whole command path.

## Implementation Notes
- Keep this task focused on one record only; do not add multi-record iteration yet.
- Do not implement fixed, public, or custom source behavior here beyond the flow needed to call the source resolver interface.
- Do not add wizard changes here.
- Prefer the smallest practical shape for the Cloudflare client boundary so later tasks can extend it.
- Reuse the config records and validation from task 3 rather than introducing a second config shape.
- Keep the terminal output path simple for now; later tasks can replace `print` with a standardized logging approach if needed.

## Verification
- Add or update focused unit tests for:
  - unchanged record is skipped
  - changed record is updated
  - source resolution happens before update
  - failure produces a single clear record result
- Run the targeted tests for the single-record update path.

## Follow-ups
- Add fixed source validation and support.
- Add public source support.
- Add custom source support.
- Expand from one record to all configured records.
- Add proxied and TTL rule handling.
- Carry the remaining source-specific acceptance criteria into the later source tasks.
