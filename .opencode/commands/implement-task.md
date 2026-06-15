---
description: Implement the selected task with focused verification
---

Implement the selected task using the frozen spec, the roadmap or task list, and the relevant task spec in `tasks/`.

Use the `implement-task` skill.

Requirements:

- Resolve the task from a `task N` reference when possible.
- If the reference is ambiguous or cannot be resolved, ask for the task spec path.
- Keep the scope to one task only.
- Inspect the relevant code paths and task context before editing.
- Generate or update unit tests as part of the implementation.
- Run the task-relevant unit tests by default.
- When the task changes CLI behavior, run the actual app entrypoint once as part of verification, not just the test suite.
- For trivial work, consider reputable free external libraries before custom implementation.
- Prefer splitting growing features into small modules: keep entrypoints thin, move shared constants into a constants module, and place wizard or run-mode placeholders in their own modules when that improves clarity.
- If the task changes module ownership or splits an entrypoint, update the related unit tests and test file names in the same task.
- If the standard task workflow applies, create the branch first from `develop` using `feature/<slug>`.
- If the user explicitly wants to work on the current branch or directly on `develop`, follow that instruction and skip branch creation.
- Before any commit or PR step, verify the diff against the intended base or current branch and make sure no unrelated files are included.
- If the current work is not happening in `develop`, commit every change relatwd with the task and open a PR.
