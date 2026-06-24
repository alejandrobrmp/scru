# Task 10: Config Wizard

## Goal

Replace the empty `new()` and `edit()` skeletons in `src/scru/wizard.py` with a screen-clearing interactive wizard that guides the user through creating or editing a YAML config via the Cloudflare API.

## Scope

- Implement `new()` to guide the user through selecting a zone, picking a DNS record, configuring source/proxied/ttl, and repeating for multiple records.
- Implement `edit()` to load the existing config, show a numbered record list, and offer add/update/remove/save operations via a persistent menu.
- Add `input_func: Callable[[str], str] = input` parameter to `new()` and `edit()` so tests can inject canned responses.
- Add `list_all_zones()` and `list_all_records(zone_id)` methods to `CloudflareClient` (for wizard zone/record browsing).
- Use screen clearing between steps (`\033[2J\033[H` ANSI escape).
- Show a breadcrumb bar at the top with mode (NEW/EDIT), current zone, and current record name.
- Breadcrumb bar must dynamically match terminal width (via `shutil.get_terminal_size`). If width < 60, switch to multi-line layout.
- Fail early with a clear message if `CLOUDFLARE_API_TOKEN` is not set.
- Keep `wizard.main()` and CLI routing unchanged (already wired and tested).
- Do not change `config.py`, `constants.py`, `cli.py`, `update.py`, or the YAML schema.
- Create `tests/test_wizard.py` with unit tests for both `new()` and `edit()` paths.

## Dependencies

- `tasks/09-cloudflare-update-rules.md`
- `tasks/03-config-model-and-yaml-io.md`
- `tasks/01-cli-skeleton.md`
- `spec/01_spec.md`

## Acceptance Criteria

### Zone & record listing (new `CloudflareClient` methods)

- `CloudflareClient.list_all_zones()` calls `GET /zones` with `per_page=50` and returns all zones as a list of dicts.
- `CloudflareClient.list_all_records(zone_id)` calls `GET /zones/{zone_id}/dns_records` with `per_page=50` and `type=A` and returns all A records as a list of dicts.
- Existing methods (`get_record`, `get_zone_id`, `list_zones`, `list_records`) remain unchanged.
- Both new methods raise `CloudflareClientError` on failure.

### Token validation

- At the start of `new()` and `edit()`, check the env var. If missing, print a single error line and return immediately.
- Error format: `✘ CLOUDFLARE_API_TOKEN is not set — set it and try again.`
- Do not print a breadcrumb bar on token-missing error; just the error line.

### `new()` wizard flow

Each step clears the screen and prints the breadcrumb bar before the section content.

**Page 1 — Select zone:**
- Fetch zones via `CloudflareClient.list_all_zones()`.
- Show zone name and zone ID side by side, numbered.
- Prompt: `Select zone (1-N) [1]:`.
- If API call fails, print the error and re-prompt the menu.

**Page 2 — Select record:**
- Fetch A records via `CloudflareClient.list_all_records(zone_id)`.
- Show record names numbered.
- If no A records exist, show `(no A records found)` and still allow typing a new name.
- Prompt: `Select record (1-N) or type a new name:`.

**Page 3 — Configure source:**
```
Source type:
  1. fixed   — enter an IP manually
  2. public  — use my current public IP
  3. custom  — run a command
Select (1-3) [2]:
```
- If fixed: prompt `Fixed IPv4:`.
- If custom: prompt `Command:`.
- If public: skip.

**Page 4 — Proxied & TTL:**
- Prompt: `Proxied? (y/n) [n]:`.
- Prompt: `TTL in seconds (blank=omit):`.
- If proxied is yes and ttl is entered, print warning: `⚠ warning: ttl is ignored for proxied records` below the ttl prompt.

**Page 5 — Record summary & add another:**
- Show record summary: `<name> @ <zone_name>` with source, proxied, ttl.
- Prompt: `Add another record? (y/N):`.
- If yes, loop back to page 1 (zone selection again, to support multi-zone).
- If no, call `save_config()` and print: `✔ Config saved to ~/.config/scru/config.yaml`.

### `edit()` wizard flow

Each menu action clears the screen and prints the breadcrumb + content.

**Menu page:**
```
── Configured records ─────────────────────────────────────────

  1. www @ example.com   (public  | proxied: yes | ttl: auto)
  2. api @ example.com   (custom  | proxied: no  | ttl: 300)

── Menu ───────────────────────────────────────────────────────

  a      Add a new record
  u <n>  Update record <n>
  d <n>  Delete record <n>
  q      Save and quit
```

- `a` — enter the same add-record sub-flow as `new()` pages 1-4, then return to menu.
- `u <n>` — re-prompt all fields with current values as defaults; blank = keep.
- `d <n>` — remove record, re-number, return to menu.
- `q` — call `save_config()` and print: `✔ Config saved to ~/.config/scru/config.yaml`. Exit.
- If all records are deleted, print: `No records left` and do not save.
- Invalid menu input re-prints the menu.

### Breadcrumb bar

**Wide terminal (>= 60 cols):**
```
╔══════════════════════════════════════════════╗
║  NEW  ·  example.com  ·  www                ║
╚══════════════════════════════════════════════╝
```
Inside line: `  {mode}  ·  {zone_name}  ·  {record_name}  ` (left-padded, centered, or left-aligned — choice left to implementation).

**Narrow terminal (< 60 cols):**
```
╔══════════════════════════╗
║  NEW                     ║
║  zone: example.com       ║
║  record: www             ║
╚══════════════════════════╝
```

- Box width = `min(terminal_width - 1, 80)`.
- The `zone` line omitted when no zone selected.
- The `record` line omitted when no record selected.
- In edit mode, breadcrumb shows current selection context (last zone/record operated on, or `—` for unset).

### General

- `input_func( prompt )` is used for all user prompts (defaults to `builtins.input`).
- All prompts print to stdout via `input_func` (no direct `print` for prompts).
- Screen clearing: `print("\033[2J\033[H", end="")`.
- Section headers use `──` as separators, dynamically sized to match content width.
- All existing CLI and wizard-routing tests continue to pass.
- Unit tests in `tests/test_wizard.py` cover:
  - `new()` with one fixed record.
  - `new()` with two records (one public, one custom).
  - `new()` with proxied+ttl warning.
  - `new()` with token missing.
  - `edit()` add one record.
  - `edit()` update a record (blank = keep).
  - `edit()` delete a record.
  - `edit()` save and quit.
  - `edit()` delete last record and see no-save message.

## Implementation Notes

- Keep `wizard.main()` signature unchanged (already wired in CLI, already tested).
- Add `input_func` to `new()` and `edit()` only; do not change `main()`.
- Use `load_config()` and `save_config()` from `config.py` for all I/O.
- Use the existing `SourceConfig`, `RecordConfig`, and `Config` constructors, not raw dicts.
- For zone and record selection, parse user input as int and index into the API response.
- For "type a new name" in record selection, treat non-integer input as a record name.
- The record summary line in edit mode shows: `<name> @ <zone_name>   (<source_type> | proxied: <yes/no> | ttl: <value/auto>)`.
- Import `CloudflareClient` from `cloudflare.py` inside `new()`/`edit()` (not at module level) so wizard module can be imported without the token.
- Use `shutil.get_terminal_size()` for dynamic width.
- Build the bounding box top/bottom lines with the correct number of `═` chars based on width.
- For the breadcrumb line, left-align the content with 2 spaces padding inside the box.
- Split the screen-clearing helper into a small private function (`_clear_screen()`) for testability.
- Reuse existing tests in `test_cli.py` unchanged.

## Verification

- Run `pytest tests/test_wizard.py` and confirm all new tests pass.
- Run `pytest` and confirm no regressions.
- Manually run `scru config` with a valid `CLOUDFLARE_API_TOKEN` and verify the full new() flow end to end.
- Manually delete the config, re-create it, then run `scru config` again and verify the edit() flow.
- Verify that `✘ CLOUDFLARE_API_TOKEN is not set` appears when token is missing.

## Follow-ups

- Add IPv4 validation to the fixed-source wizard prompt if runtime errors become common.
- Consider pagination support in `list_all_zones()` and `list_all_records()` if users have 50+ zones or records.