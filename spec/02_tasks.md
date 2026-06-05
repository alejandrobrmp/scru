# SCRU Task Roadmap

This file is only the high-level roadmap.

Each roadmap item must be refined into its own spec under `tasks/` before execution.

Workflow:

1. Refine task 1 into a `tasks/` spec.
2. The developer executes task 1 from that spec.
3. Refine task 2 using the result of task 1.
4. The developer executes task 2 from that spec.
5. Repeat for the remaining tasks.

1. CLI skeleton
- Add `scru` and `scru config` entry points.
- Detect config path and missing config state.
- Route to either run mode or wizard.

2. Config model and YAML IO
- Define the YAML schema for token env var, zones, records, source, `proxied`, and `ttl`.
- Load and save config in the per-user config directory.
- Validate required fields early.

3. One-record update slice
- Implement the record update flow for a single `A` record.
- Resolve source IPv4, fetch Cloudflare state, skip if unchanged, update if needed.
- Print one clear line for success, skip, or failure.

4. Fixed source support
- Support user-provided IPv4 input as a record source.
- Validate IPv4 format before update.

5. Public source support
- Fetch current public IPv4 of the machine.
- Plug it into the same record update flow.

6. Custom source support
- Run a user command and capture exact stdout.
- Enforce 10-second timeout.
- Fail only that record on command errors or invalid output.

7. Multi-record and multi-zone execution
- Iterate all configured records.
- Keep failures isolated per record.
- Report each result on its own line.

8. Cloudflare update rules
- Support updating `proxied`.
- Respect Cloudflare TTL behavior.
- Avoid fighting provider-enforced TTL values.
- Keep unchanged records skipped.

9. Config wizard
- Create config when missing.
- Edit existing config when present.
- Add, update, and remove records.
- Support multiple zones and per-record source selection.

10. Tests and packaging
- Add unit tests for config, sources, skip logic, and update behavior.
- Cover per-record failure isolation.
- Add Linux packaging/build workflow.
