# Task 11b: Release CI and Build Packaging

## Goal

Add a GitHub Actions release workflow triggered by `X.X.X` tags that builds wheel and sdist artifacts, runs unit tests, and creates a GitHub Release.

## Scope

- Add `.github/workflows/release.yml`.
- No Makefile.
- No README changes (deferred to 11a).
- No application code changes.
- No PyPI publishing (not in spec).

## Dependencies

- `tasks/11a-documentation.md`
- `spec/01_spec.md`
- `main` must include all completed tasks merged from `develop`.

## Acceptance Criteria

### Workflow trigger

- The workflow triggers on push of tags matching `*.*.*` (e.g., `0.1.0`, `0.2.0`).
- Triggers only on tags, not on branch pushes or PRs.

### Build

- The workflow installs `build` and runs `python -m build`.
- Both a wheel (`.whl`) and source distribution (`.tar.gz`) are produced in `dist/`.
- `pyproject.toml` version is bumped before tagging (manual step, not automated).

### Test gate

- Unit tests run before the release is created: `pip install ".[test]" && python -m pytest tests/ --ignore=tests/integration`.
- If tests fail, the release is **not** created (the workflow fails).

### GitHub Release

- A GitHub Release is created using [`softprops/action-gh-release@v2`](https://github.com/softprops/action-gh-release).
- Release title is the tag name.
- Both artifacts from `dist/**/*` are attached to the release.
- Release body is auto-generated (changelog not required).

### No regressions

- Existing workflows (`pr-validation.yml`, `unit-tests.yml`, `integration-tests.yml`) remain unchanged and continue to work.

## Implementation Notes

- Use the same Python version (`3.11`) and OS (`ubuntu-latest`) as the existing unit-tests workflow.
- The `files` glob for `action-gh-release` should match `dist/**` (or `dist/*.whl` and `dist/*.tar.gz` explicitly).
- The workflow does **not** need a `workflow_dispatch` trigger — it runs only on tags.
- The checkout step should check out the tag, not a specific branch. `actions/checkout@v4` handles this automatically for tag-triggered workflows.
- The release is tied to the tagged commit on `main` per the spec's release flow.
- Version bumps in `pyproject.toml` are manual — the developer edits the version field before tagging.

## Verification

1. Push a test tag from `main` (e.g., `0.2.0-rc1`):
   ```
   git checkout main
   git tag 0.2.0-rc1
   git push origin 0.2.0-rc1
   ```
2. Confirm the workflow runs in the GitHub Actions tab.
3. Confirm unit tests pass and both artifacts are produced.
4. Confirm a GitHub Release appears with the tag name and both `.whl` and `.tar.gz` attached.
5. Delete the test tag and release after verification:
   ```
   git push --delete origin 0.2.0-rc1
   git tag -d 0.2.0-rc1
   ```
   (Delete the GitHub Release manually via the Releases page.)

## Follow-ups

- First real release: bump version in `pyproject.toml`, tag on `main`, push.
- Consider auto-generating release notes from merged PRs in the future.