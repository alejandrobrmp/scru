# Task 1: CLI Skeleton

## Goal
Create the minimal CLI entrypoint structure for SCRU.

## Scope
- Add `scru` and `scru config` commands only.
- Detect the config file at `~/.config/scru/config.yaml`.
- Route `scru` to run mode when config exists.
- Route `scru` to the wizard placeholder when config is missing.
- Route `scru config` to the wizard placeholder.
- Show the user message `No config file found, create one first.` when config is missing.
- Add a focused unit test for the routing decision.

## Dependencies
- `spec/01_spec.md`
- `spec/02_tasks.md`
- `tasks/README.md`

## Acceptance Criteria
- `scru` and `scru config` both exist.
- Missing config at `~/.config/scru/config.yaml` prints the message and opens the wizard placeholder.
- Existing config routes `scru` to run mode.
- `scru config` always routes to the wizard placeholder.
- Two separate wizard placeholders exist: `new` and `edit`.
- A unit test covers the missing-vs-present config routing.

## Implementation Notes
- Keep this thin and explicit.
- Treat missing file as the only missing-config case for now.
- Leave a TODO to later handle unreadable or invalid config files.
- Keep the command surface limited to these two commands.
- Use Linux config directory conventions for the user config path.

## Verification
- Run the focused unit test for CLI routing.

## Follow-ups
- Add unreadable file and bad format handling later.
- Build the wizard behavior in a later task.
