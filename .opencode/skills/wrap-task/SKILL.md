---
name: wrap-task
description: Wrap up completed task work or review-driven follow-up. Use when the branch is ready to be summarized, documented, and optionally committed or PR'd.
---

# Wrap Task

Use this skill when the task implementation is complete or when review feedback on that task has already been addressed and the branch needs to be finalized.

## Goal

Turn completed task work into a clean handoff for the current branch context.

## Process

1. Inspect the changes made since the last task update or since the review feedback.
2. If the task has an open PR, inspect its issue comments, reviews, and review threads before deciding the wrap is complete.
3. Summarize the work clearly.
4. Update the task spec if the implementation changed any recorded details.
5. Save any important technical details to memory.
6. Decide the finish mode from the user request:
   - Standard task workflow: commit the final changes and open or refresh the draft pull request.
   - Explicit user override: keep working directly on the current branch or on `develop` and stop after verification and summary.
7. Before any commit or PR step, confirm `git status` and the diff against the intended base or current branch contain only the intended changes.

## Rules

- This is the only post-implementation workflow; review-fix iterations use the same loop.
- If a PR exists, do not wrap blindly: check whether comments or review threads still require action.
- Keep the summary factual and concise.
- Only update the task spec when the implementation adds or changes relevant details.
- Save non-obvious technical details, decisions, or gotchas to memory.
- Do not commit or open a PR unless the user asked for that delivery step.
- If the work is not actually complete, stop and say what remains.

## Output

Execute the checks and updates first.

Summaries should reflect the finished state.
