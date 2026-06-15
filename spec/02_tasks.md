# SCRU Task Roadmap

This file is only the high-level roadmap.

Each roadmap item must be refined into its own spec under `tasks/` before execution.

Workflow:

1. Refine task 1 into a `tasks/` spec.
2. The developer executes task 1 from that spec.
3. Refine task 2 into a `tasks/` spec.
4. The developer executes task 2 from that spec.
5. Refine task 3 using the result of task 2.
6. The developer executes task 3 from that spec.
7. Repeat for the remaining tasks.

1. CLI skeleton
- Add `scru` and `scru config` entry points.
- Detect config path and missing config state.
- Route to either run mode or wizard.

2. PR unit test workflow
- Add a GitHub Actions workflow for pull requests.
- Run the unit test command on every PR.
- Fail the workflow when tests fail.

3. Config model and YAML IO
- Define the YAML schema for token env var, zones, records, source, `proxied`, and `ttl`.
- Load and save config in the per-user config directory.
- Validate required fields early.

4. One-record update slice
- Implement the record update flow for a single `A` record.
- Resolve source IPv4, fetch Cloudflare state, skip if unchanged, update if needed.
- Print one clear line for success, skip, or failure.

5. Fixed source support
- Support user-provided IPv4 input as a record source.
- Validate IPv4 format before update.

5_1. Integration tests
- Execute the app against real Cloudflare with positive and negative cases.
- Use a local untracked `.env` for integration-only secrets and test values.
- Store scenario YAMLs under `tests/integration/cases/` and keep zone/record names out of plain text.
- Copy config YAMLs into the config path from `src/scru/constants.py` and clean them up after each case.
- Create and remove Cloudflare resources per test, including crash cleanup.

6. Public source support
- Fetch current public IPv4 of the machine.
- Plug it into the same record update flow.

7. Custom source support
- Run a user command and capture exact stdout.
- Enforce 10-second timeout.
- Fail only that record on command errors or invalid output.

8. Multi-record and multi-zone execution
- Iterate all configured records.
- Keep failures isolated per record.
- Report each result on its own line.

9. Cloudflare update rules
- Support updating `proxied`.
- Respect Cloudflare TTL behavior.
- Avoid fighting provider-enforced TTL values.
- Keep unchanged records skipped.

10. Config wizard
- Create config when missing.
- Edit existing config when present.
- Add, update, and remove records.
- Support multiple zones and per-record source selection.

11. Tests and packaging
- Add unit tests for config, sources, skip logic, and update behavior.
- Cover per-record failure isolation.
- Add Linux packaging/build workflow.
