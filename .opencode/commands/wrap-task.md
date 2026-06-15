---
description: Finalize completed work or review fixes on the current branch
---

Wrap the completed task work, or a review-driven follow-up on that task, using the current branch changes, the task spec, and the latest implementation details.

Use the `wrap-task` skill.

Requirements:

- Inspect the changes made since the last task update or since the review feedback.
- If the task has an open PR, inspect its comments and review threads before deciding the wrap is complete.
- Summarize the implementation or fixes clearly.
- Update the task spec if the recorded task details need to change.
- Save any important technical detail to memory.
- Treat review-fix work as part of this same wrap loop; do not require a separate command.
- If the user asked for branch/PR delivery, commit the final changes to the current branch and open or refresh the draft pull request.
- If the user explicitly asked to keep working directly on the current branch or on `develop`, stop after verification and summary.

If the work is not actually complete, stop and ask what remains before wrapping.
