---
name: refine-task
description: Refine task specs, roadmap items, and next-step documentation. Use when creating or tightening any task spec from a roadmap and prior task outcome.
---

# Refine Task

Use this skill when preparing a task spec in `tasks/`.

## Goal

Create a narrow, executable spec for one task at a time.

## Process

1. Read the frozen product spec.
2. Read the roadmap or task list.
3. Read the latest completed task spec, if one exists.
4. Refine only the next task, not the whole roadmap.
5. Keep the spec small, explicit, and manually executable by the developer.
6. If any task detail is uncertain, ask the user and wait for the answer before writing the spec.
7. Write the new spec to `tasks/<number>-<slug>.md`.

## Required Sections

Each task spec should include:

- `Goal`
- `Scope`
- `Dependencies`
- `Acceptance Criteria`
- `Implementation Notes`
- `Verification`
- `Follow-ups`

## Rules

- Keep the roadmap file as roadmap-only.
- Do not automate execution.
- The developer executes each step manually.
- Use the previous task result to refine the next task.
- Avoid broad scope expansion.
- Keep the task aligned with the frozen spec.
- When a task can be solved with a reputable free external library and the work is trivial, prefer that option over custom code.
- Carry forward any implementation boundaries learned from the previous task.
- If the next task depends on a structural refactor from the previous one, state that dependency explicitly in the spec.

## Output

When refining, produce the spec content first, then mention the file path to write.
