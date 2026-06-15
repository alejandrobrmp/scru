# Task 5_1: Integration Tests

## Goal
Add real Cloudflare integration tests that execute SCRU end to end with both positive and negative cases.

## Scope
- Create a dedicated integration test suite.
- Store scenario YAML files under `tests/integration/cases/`.
- Use a local `.env` file for integration-only secrets and token values.
- Load the Cloudflare token and any test-only secrets from that `.env`.
- Resolve the zone by name and use environment variables in the YAML cases for zone and record names instead of plain text values.
- Copy each config YAML into the config path defined in `src/scru/constants.py` before running a case.
- Clean up copied config files after each case.
- Create Cloudflare resources in each test and delete them afterward.
- Handle crash or hard-failure cleanup so leftover Cloudflare resources can still be removed.

## Dependencies
- `tasks/05-fixed-source-support.md`
- `spec/01_spec.md`
- `spec/02_tasks.md`

## Acceptance Criteria
- The application is exercised end to end against real Cloudflare.
- Positive and negative integration cases are covered.
- YAML case files do not contain real zone or record names in plain text.
- Each test creates and cleans up its own Cloudflare resources.
- Recovery cleanup exists for cases where a test crashes or fails unrecoverably.
- Config files copied into the user config path are removed after the test finishes.

## Implementation Notes
- Keep integration fixtures separate from unit test fixtures.
- Use `tests/integration/cases/` for all scenario YAMLs.
- Treat `src/scru/constants.py::CONFIG_PATH` as the source of truth for the config location.
- Add `.gitignore` coverage for the real integration `.env` during implementation, and keep any checked-in example file separate if it helps document required variables.
- Prefer dedicated Cloudflare test resources over production resources.
- Resolve the target zone ID from the configured zone name during test setup.

## Verification
- Run the integration suite against Cloudflare real credentials.
- Verify at least one passing case and one failing case.
- Verify cleanup leaves no copied config files or Cloudflare leftovers.

## Follow-ups
- Add more scenario coverage if new update behaviors appear.
- Expand cleanup tooling if another failure mode appears in practice.
