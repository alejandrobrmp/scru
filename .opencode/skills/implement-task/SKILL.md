---
name: implement-task
description: Implement a task end to end from branch creation to draft pull request. Use when working from a task spec in `tasks/` or a `task N` reference.
---

# Implement Task

Use this skill when executing one task from `tasks/`.

## Goal

Create a complete manual workflow for one task: branch, implement, test, commit, push, and open a draft PR.

## Process

1. Read the frozen product spec.
2. Read the roadmap or task list.
3. Resolve the target task from `task N` when possible, otherwise ask for the task spec path.
4. Read the latest completed task spec, if one exists.
5. Create a branch from `develop` before making changes.
6. Use `feature/<slug>` for the branch name.
7. Inspect the relevant code paths and task context.
8. When shell commands are needed on this Windows host, use WSL and prefer the Ubuntu distro.
9. Use sub-agents when they reduce context usage or speed up focused work.
10. Prefer `explore` for targeted discovery and reads.
11. Prefer `general` for multi-step synthesis, implementation planning, and isolated coding chunks.
12. Prefer smaller or faster models for narrow search and classification work.
13. Prefer stronger models for synthesis, edge cases, and final review.
14. Check `Context7` when the task depends on external library, framework, SDK, or CLI documentation.
15. Implement the task.
16. Add or update unit tests for the changed behavior.
17. Run the task-relevant unit tests by default.
18. Fix failures until the task passes.
19. Commit all changes unless the user says otherwise.
20. Push the branch.
21. Open a draft pull request back to `develop`.

## Required Sections for a Task Plan

When outlining the work, keep it explicit and small:

- Goal
- Scope
- Dependencies
- Implementation Steps
- Testing
- Failure Handling
- Follow-ups

## Rules

- Keep the workflow generic.
- Do not assume a specific feature domain.
- Keep the task to one spec only.
- Create the branch first.
- Use WSL Ubuntu for shell-based work on this Windows machine.
- Preserve the frozen spec.
- Use the previous task result to shape the current task.
- Keep changes minimal and focused.
- Default to task-relevant unit tests only unless the task spec says otherwise.
- Commit everything by default.
- Open a draft PR by default.

## Output

When executing, produce the implementation plan first, then proceed with the work.
