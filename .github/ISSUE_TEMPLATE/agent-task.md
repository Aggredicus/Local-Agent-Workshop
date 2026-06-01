---
name: Agent task
description: Standard execution contract for agent-executable work
title: "[Agent Task]: "
labels: []
assignees: []
---

## Summary

<!-- Describe the task in one or two paragraphs. -->

## Inputs

- Required source files:
- Required existing docs:
- Required schemas:
- Required issue dependencies:
- Relevant reports/artifacts:

## Outputs

- Files to add/update:
- Reports/artifacts to generate:
- Schemas to validate:
- Documentation links to update:

## Evidence required

- Test command or validation command:
- Expected report path:
- Required SUMMARY block:
- Chronicle event required? yes/no
- HyperKanban transition required? yes/no
- Review packet or handoff required? yes/no

## Stop conditions

Stop and create a handoff if:

- [ ] Required context is missing.
- [ ] Task scope is ambiguous.
- [ ] A dependency issue is incomplete.
- [ ] A risk boundary is reached.
- [ ] Evidence cannot be produced.
- [ ] The task would require secrets.
- [ ] The task would require protected branch mutation.
- [ ] The task would require public endpoint exposure.
- [ ] The task would require destructive host or infrastructure mutation.
- [ ] The task would bypass human approval, lease, budget, or review boundaries.

## Non-goals

- Do not ...
- Do not ...
- Do not ...

## Agent-ready checklist

- [ ] Objective is clear.
- [ ] Eligible role or roles are clear.
- [ ] Scope is bounded.
- [ ] Allowed paths are listed.
- [ ] Forbidden paths are listed.
- [ ] Risk level is understood.
- [ ] Budget or effort boundary is defined.
- [ ] Lease requirement is defined if mutation is allowed.
- [ ] Required evidence is listed.
- [ ] Acceptance criteria are testable.
- [ ] Stop conditions are listed.
- [ ] Handoff requirement is clear.

## Human-ready checklist

- [ ] Summary of changes is present.
- [ ] Changed files are listed.
- [ ] Evidence paths are provided.
- [ ] Checks run are listed.
- [ ] Failures or skipped checks are explained.
- [ ] Known risks are documented.
- [ ] Follow-up recommendations are included.
- [ ] Explicit human decision needed is stated.

## Acceptance criteria

- [ ] ...
- [ ] ...
- [ ] ...

## Handoff format

```text
issue:
role:
branch/worktree:
summary:
changed files:
evidence paths:
checks run:
blockers:
risks:
next recommended action:
human decision needed:
```
