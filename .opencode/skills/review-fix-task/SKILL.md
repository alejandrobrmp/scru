---
name: review-fix-task
description: Fix PR review comments and re-wrap the task. Use when a draft PR already exists and comments need to be resolved, summarized, captured in memory, and re-committed.
---

# Review Fix Task

Use this skill when a draft PR has review comments that need to be addressed.

## Goal

Resolve review feedback and return the task to a review-ready draft PR state.

## Process

1. Read the PR comments and identify the required fixes.
2. Make the smallest correct changes.
3. Inspect the resulting changes.
4. Summarize the fixes.
5. Update the task spec if the task record should reflect the new detail.
6. Save any important technical detail to memory.
7. Commit the fixes to the current branch.
8. Refresh the draft pull request.

## Rules

- Address only the feedback that applies to the task.
- Keep the changes minimal and focused.
- Update tests if needed.
- Preserve the intent of the existing task spec unless a correction is required.
- Save any useful technical detail discovered while fixing the review.
- Include deleted or untracked files in the commit.

## Output

When fixing review feedback, produce the fix summary first, then perform the updates and PR step.
