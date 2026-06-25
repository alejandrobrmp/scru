# Task Specs

This directory holds one refined spec per roadmap item.

Rules:

- `spec/02_tasks.md` stays as the roadmap only.
- Before execution, each roadmap item must be expanded into its own file here.
- Task specs should be small and focused on one task only.
- Each new task spec should use the outcome of the previous task when refining the next one.
- The specs support a manual workflow; the developer executes each step.
- Use the same pattern for any future roadmap, not just this project's current tasks.

Suggested format for each task file:

1. `Goal`
2. `Scope`
3. `Dependencies`
4. `Acceptance Criteria`
5. `Implementation Notes`
6. `Verification`
7. `Follow-ups`

Naming:

- Use a stable, numbered filename per roadmap item, such as `01-cli-skeleton.md`.
- Keep the filename aligned with the roadmap order.

Recommended workflow:

1. Read the frozen product spec.
2. Read the roadmap or task list.
3. Read the latest completed task spec, if one exists.
4. Refine the next task spec.
5. Execute that task manually.
6. Repeat for the next task.
