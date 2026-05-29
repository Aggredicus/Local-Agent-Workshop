# Workflow: /design-first

## Purpose

Generate a design-first report before implementation begins.

This workflow calls:

```text
skills/design-first/SKILL.md
templates/reports/design-first-output.html.tmpl
schemas/design-first-report.schema.json
```

## Entry command

```sh
workshop design-first "<request>"
```

Future examples:

```sh
workshop design-first "Implement the first review-card generator"
workshop design-first "Design Telegram escalation adapter"
workshop design-first "Refactor branch policy enforcement"
```

## Instruction hierarchy

This workflow is not the canonical policy source. It must route agents through:

```text
AGENTS.md / CLAUDE.md / CODEX.md / Cursor rules
  ↓
me.md
  ↓
skills/design-first/SKILL.md
  ↓
this workflow
```

## Required inputs

- request
- repo path
- current branch
- run ID
- agent name
- optional risk hint
- optional target files

## Required outputs

```text
reports/design-first/<run-id>.html
chronicle/events/<event-id>.json
reviews/pending/<review-id>.json, if implementation is recommended
```

## Workflow steps

1. Read `me.md`.
2. Read `skills/design-first/SKILL.md`.
3. Load governance, protocol, architecture, schema, and plan docs.
4. Frame the problem.
5. Compare architecture options.
6. Choose a recommended design.
7. Classify risk.
8. Define implementation slices.
9. Define verification commands.
10. Generate the HTML design-first report.
11. Emit a Chronicle event.
12. Create or update a review card if the design recommends implementation.
13. Return next action.

## Status outcomes

The workflow must return one of:

```text
ready_for_implementation
needs_human_decision
needs_more_context
blocked_by_risk
blocked_by_missing_docs
```

## Human approval triggers

Pause before implementation if:

- live credentials are needed,
- production side effects are possible,
- payment/auth/secrets behavior changes require approval,
- protected branches would be touched,
- or the design changes repository governance.
