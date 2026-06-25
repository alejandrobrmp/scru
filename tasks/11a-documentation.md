# Task 11a: README and Documentation

## Goal

Replace the stub README with complete user-facing documentation covering installation, configuration, commands, source types, and examples.

## Scope

- Rewrite `README.md` from scratch.
- Do **not** create additional documentation files (no `docs/` directory, no man pages).
- Do **not** change application code, the frozen spec, or CI workflows.
- Do **not** add build/release instructions (deferred to 11b if needed).

## Dependencies

- `tasks/10-config-wizard.md` (latest completed task — all features are implemented)
- `spec/01_spec.md`

## Acceptance Criteria

### Content

Every feature from the frozen spec is documented in user-facing language:

1. **Title and tagline** — what SCRU does and why you'd use it.
2. **Requirements** — Python 3.11+, Linux, Cloudflare API token.
3. **Installation** — `pip install scru` and from-source instructions.
4. **Quick Start** — set the env var, run `scru config`, run `scru`.
5. **Commands** — `scru` (run mode) and `scru config` (wizard mode) with behavior described.
6. **Configuration** — YAML schema explained: `api_token_env`, zones, records, `name`, `type`, `content`/`command`, `proxied`, `ttl`.
7. **Source types** — fixed, public, and custom with usage examples for each.
8. **Cloudflare TTL and proxied behavior** — proxied records ignore TTL, provider-enforced TTL is respected.
9. **Error behavior** — per-record failure isolation, unchanged record skipping.
10. **Examples** — at least one end-to-end example with sample YAML and CLI output.

### Format

- Valid GitHub-flavored Markdown.
- Sections use standard `##` headers.
- Code blocks use fenced syntax with appropriate language tags (`yaml`, `bash`, `text`).
- No stale content from the original stub (remove the "intentionally basic" disclaimer line).

### Accuracy

- All documented behaviors match the frozen spec and current implementation.
- No claims about features that are not yet implemented.
- Config YAML example references `api_token_env` (env var name) correctly.
- The wizard flow is described as interactive, not automated.

## Implementation Notes

- The existing README is a 16-line stub — replace entirely, don't patch.
- Reference the frozen spec for behavior accuracy; reference source code if any behavior is unclear.
- Configuration YAML example should reflect the actual schema from `config.py`.
- Use `~/.config/scru/config.yaml` as the config path when describing file locations.
- The token env var name in examples should match what `constants.py` defines.

## Verification

- Render the README in a GitHub-flavored Markdown viewer.
- Cross-reference every section against `spec/01_spec.md` — no missing features.
- Confirm no broken references or dead links.
- Run through the Quick Start steps mentally as a new user — no gaps.

## Follow-ups

- Task 11b may add build instructions to README after packaging is done.