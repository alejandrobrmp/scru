# SCRU

Simple Cloudflare Record Updater.

## Overview

SCRU is a lightweight Linux-only CLI for updating Cloudflare `A` records from a selected IPv4 source.

## Goals

- Stay simple to understand
- Be fast to build
- Require minimal setup
- Handle multiple records across multiple zones
- Keep failures isolated per record

## Non-Goals

- No Windows or macOS support
- No record types other than `A`
- No secret storage
- No complex sync engine
- No web UI

## Commands

### `scru`

Runs all configured updates.

Behavior:

- If config is missing, launch the config wizard
- Otherwise process all configured records
- Continue after per-record failures

### `scru config`

Launches the config wizard.

Behavior:

- Create config if missing
- Edit existing config if present
- Support adding, updating, and removing records

## Configuration

Format:

- YAML

Location:

- Per-user config directory

Contents:

- Cloudflare API token reference via environment variable
- Record definitions
- Zone IDs
- Record names
- Source configuration
- `proxied`
- `ttl`

Config may contain multiple records from multiple zones.

## Authentication

- Cloudflare API Token must be provided via environment variable
- No interactive token storage
- No global API key support

## Supported Sources

### Fixed

Uses a user-provided IPv4 address.

### Public

Uses the current machine public IPv4.

### Custom

Runs a user command and uses its exact stdout as the IPv4.

Rules:

- Output must be exactly one valid IPv4 string
- Timeout is 10 seconds
- If the command fails, only that record fails
- Other records continue

## Update Rules

- Only `A` records are supported
- Skip updates when the current value is unchanged
- Update `proxied` when configured
- Update `ttl` when configured and allowed by Cloudflare

Cloudflare TTL rules must be respected:

- If Cloudflare enforces a TTL value for a given record state, SCRU must not fight it
- When proxied records impose provider-side TTL constraints, SCRU should accept Cloudflare behavior

## Execution Model

For each configured record:

1. Resolve the source IPv4
2. Validate it
3. Fetch current Cloudflare record state
4. Skip if unchanged
5. Update record if needed
6. Report success or failure

Failures:

- One record failure must not stop the rest
- Errors should be clear and short

## Wizard

The config wizard should:

- Ask only for required information
- Keep prompts simple
- Support multiple records
- Support multiple zones
- Let the user choose source type per record

## Output

- Human-readable CLI output
- One line per record result
- Show skipped, updated, and failed states
- Avoid noisy debug output by default

## Packaging

- Linux package only
- Python implementation
- Keep dependencies minimal

## Git And Branching

- `main` is the protected production branch
- No direct pushes or commits to `main`
- `develop` is the integration branch
- `develop` is not protected, but it should not be used for routine direct pushes or commits
- Every task starts from a branch created off `develop`
- Each task branch is merged back through a pull request
- Branches should stay short-lived and task-focused

## Workflow

1. Create a branch from `develop`
2. Implement the task
3. Open a pull request back to `develop`
4. Merge after review and tests pass

## CI And Releases

### Pull Request Workflow

- Runs on every pull request
- Executes unit tests
- Must pass before merge

### Release Workflow

- Runs on each release
- Can also be run manually if needed
- Builds the app artifacts

### Release Flow

- Releases are cut from `main`
- Release tags use the format `X.X.X`
- A release is created from a tag on `main`
- Release builds should be tied to that tag

## Security

- API token comes from environment only
- Do not print secrets
- Do not persist secrets in config

## Acceptance Criteria

- `scru` updates all configured records
- `scru config` creates or edits YAML config
- Multiple records and zones are supported
- Fixed, public, and custom sources work
- Unchanged records are skipped
- Custom source failures affect only that record
- Only `A` records are updated
- TTL and proxied settings respect Cloudflare rules
