# Task 3: Config Model and YAML IO

## Goal
Define and implement the minimal config schema and YAML load/save path for SCRU.

## Scope
- Define the config structure for:
  - records
  - source config
  - `proxied`
  - `ttl`
- Load config from `~/.config/scru/config.yaml`.
- Save config back to the same path.
- Validate required fields before the config is used.
- Keep the task limited to config data and YAML IO only.

## Dependencies
- `tasks/01-cli-skeleton.md`
- `tasks/02-pr-unit-test-workflow.md`
- `spec/01_spec.md`
- `spec/02_tasks.md`

## Acceptance Criteria
- The config schema is minimal and records-only.
- Config can be read from `~/.config/scru/config.yaml`.
- Config can be written back to disk in YAML format.
- Missing required fields are rejected early with a clear error.
- The implementation supports multiple records.
- The config model is usable by later update and wizard tasks.

## Implementation Notes
- Keep the schema small and explicit.
- Do not implement update execution or wizard interaction here.
- Treat the config file path from task 1 as the canonical location.
- Prefer one clear validation path over layered abstractions.
- Keep source config flexible enough for later fixed, public, and custom source tasks, but do not implement source behavior yet.
- Use PyYAML for load/save instead of manual YAML parsing.
- Treat the Cloudflare token env var as fixed at `CLOUDFLARE_API_TOKEN`.
- Record entries already carry zone membership, so there is no top-level zones collection.

## Verification
- Add or update focused unit tests for:
  - load from YAML
  - save to YAML
  - missing required fields
  - multiple records parsing
- Run the targeted config tests.

## Follow-ups
- Wire this model into record update execution.
- Add wizard creation/edit flows.
- Add source-specific behavior in later tasks.
