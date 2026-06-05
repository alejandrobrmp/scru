---
description: Implement the selected task end to end
---

Implement the selected task using the frozen spec, the roadmap or task list, and the latest completed task spec in `tasks/`.

Use the `implement-task` skill.

Requirements:

- Resolve the task from a `task N` reference when possible.
- If the reference is ambiguous or cannot be resolved, ask for the task spec path.
- Create the branch first, from `develop`, using `feature/<slug>`.
- Keep the scope to one task only.
- Generate or update unit tests as part of the implementation.
- Run the task-relevant unit tests by default.
- Commit all changes unless the user says otherwise.
- Open a draft pull request back to `develop`.
