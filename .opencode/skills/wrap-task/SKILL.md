---
name: wrap-task
description: Wrap up task work after implementation is done. Use when the PR is ready to be reviewed and needs a final summary, task update, memory capture, commit, and draft PR.
---

# Wrap Task

Use this skill when the task implementation is complete and the branch needs to be prepared for review.

## Goal

Turn completed work into a clean review-ready draft PR.

## Process

1. Inspect the changes made since the last task update.
2. Summarize the work clearly.
3. Update the task spec if the implementation changed any recorded details.
4. Save any important technical details to memory.
5. Commit the final changes to the current branch.
6. Open or refresh the draft pull request.

## Rules

- Keep the summary factual and concise.
- Only update the task spec when the implementation adds or changes relevant details.
- Save non-obvious technical details, decisions, or gotchas to memory.
- Do not skip the commit before opening the draft PR.
- Before wrapping, confirm `git status` is clean and the branch diff against the PR base contains only the intended task changes.

## Output

When wrapping, produce the summary first, then perform the updates and PR step.
