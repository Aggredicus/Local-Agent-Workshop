# Workflow: /design-first

## Purpose

Generate a design-first report before implementation begins.

This workflow calls:

```text
skills/design-first/SKILL.md
templates/reports/design-first-output.html.tmpl
schemas/design-first-report.schema.json
```

## Future command

```sh
workshop design-first "<request>"
```

## Required outputs

```text
reports/design-first/<run-id>.html
chronicle/events/<event-id>.json
reviews/pending/<review-id>.json
```

## Workflow steps

1. Read `me.md`.
2. Read `skills/design-first/SKILL.md`.
3. Load governance, protocol, schema, and plan docs.
4. Frame the problem.
5. Compare architecture options.
6. Choose a recommended design.
7. Classify risk.
8. Define implementation slices.
9. Define verification commands.
10. Generate the HTML design-first report.
11. Emit a Chronicle event.
12. Create or update a review card if implementation is recommended.
13. Return next action.

## Status outcomes

Return one of:

```text
ready_for_implementation
needs_human_decision
needs_more_context
blocked_by_risk
blocked_by_missing_docs
```
