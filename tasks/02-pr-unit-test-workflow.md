# Task 2: PR Unit Test Workflow

## Goal
Add a GitHub Actions workflow that runs unit tests on every pull request.

## Scope
- Create a workflow under `.github/workflows/`.
- Trigger on `pull_request`.
- Run the project unit test command.
- Fail the check when tests fail.

## Dependencies
- `tasks/01-cli-skeleton.md`
- `spec/01_spec.md`
- `spec/02_tasks.md`

## Acceptance Criteria
- Every pull request starts a CI run automatically.
- The workflow executes unit tests.
- Failing tests fail the workflow.
- The check is visible on the pull request.

## Implementation Notes
- Keep the workflow minimal.
- Do not add release or packaging jobs here.
- Use the existing test command from the repository.
- Align with the spec requirement that PRs run unit tests.

## Verification
- Confirm the workflow triggers on a pull request.
- Confirm the unit test job passes when tests pass.
