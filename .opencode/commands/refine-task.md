---
description: Refine the next task spec
---

Refine the next task using the frozen spec, the roadmap or task list, and the latest completed task spec in `tasks/`.

Use the `refine-task` skill.

Requirements:

- Refine only one task.
- Keep the spec small, explicit, and manually executable by the developer.
- Use the previous task outcome to shape the next task.
- If any detail is uncertain, ask the user before writing the task spec.
- For trivial work, consider reputable free external libraries before custom implementation.
- Write the refined spec as a new file under `tasks/`.
- Keep the roadmap file as roadmap-only.

If no next task is obvious, identify the current roadmap position and ask for the target task.
