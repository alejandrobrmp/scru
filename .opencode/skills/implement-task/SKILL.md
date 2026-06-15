---
name: implement-task
description: Implement a task from `tasks/` with the minimum loop needed for the request. Use when working from a task spec in `tasks/` or a `task N` reference.
---

# Implement Task

Use this skill when executing one task from `tasks/`.

## Goal

Execute one task end to end for the current request: inspect, implement, verify, and wrap only if needed.

## Process

1. Read the frozen product spec.
2. Read the roadmap or task list.
3. Resolve the target task from `task N` when possible, otherwise ask for the task spec path.
4. Read the latest relevant task spec or previous task outcome when it adds needed context.
5. Decide the delivery mode before editing:
   - Standard task workflow: branch from `develop`, implement, verify, and prepare a draft PR.
   - Explicit user override: stay on the current branch or work directly on `develop`.
6. If the standard task workflow applies and a task branch is needed, create it from `develop` before editing and use `feature/<slug>`.
7. Inspect the relevant code paths and task context.
8. Use sub-agents only when they reduce context usage or speed up focused work.
9. Check `Context7` when the task depends on external library, framework, SDK, or CLI documentation.
10. For trivial work, consider reputable free external libraries before custom implementation.
11. Prefer small, explicit module boundaries for growing features: keep entrypoints thin, move constants to dedicated modules, and place placeholder behavior in separate modules when that clarifies ownership.
12. Implement the task.
13. Add or update unit tests for the changed behavior.
14. Run the task-relevant unit tests by default.
15. Run the actual app entrypoint at least once when the task touches CLI behavior, so the executable path is verified in addition to tests.
16. Fix failures until the task passes.
17. If the request includes delivery steps, inspect `git status` and the diff against the intended base or current branch before committing.
18. Commit, push, and open a draft PR only when the user explicitly asked for that full delivery loop.

## Rules

- Keep the workflow generic.
- Do not assume a specific feature domain.
- Keep the task to one spec only.
- Preserve the frozen spec.
- Use the previous task result to shape the current task.
- Keep changes minimal and focused.
- Default to task-relevant unit tests only unless the task spec says otherwise.
- If the task introduces a module split or rename, update the directly related unit tests and test filenames/names in the same change.
- If a file is deleted or replaced during a refactor, confirm the intended removal appears in the diff before finishing.
- When the user explicitly requests direct work on the current branch or `develop`, follow that override instead of forcing the branch/PR path.

## Output

Execute the work first.

Summaries should reflect completed edits and verification, not a speculative plan.
