# Local Agent Workshop — Design-First Template Pack

This pack contains the first version of the `/design-first` workflow assets.

## Files

```text
templates/reports/design-first-output.html.tmpl
skills/design-first/SKILL.md
workflows/design-first/WORKFLOW.md
schemas/design-first-report.schema.json
```

## Purpose

The `/design-first` workflow produces an interactive HTML report before implementation begins.

The report is designed for the fully released Local Agent Workshop structure and includes relative links to future project documents such as:

- `me.md`
- `docs/ARCHITECTURE.md`
- `docs/governance/RISK_POLICY.md`
- `docs/protocols/GRIND_PROTOCOL.md`
- `schemas/event.schema.json`
- `schemas/review-card.schema.json`

## Recommended install location

Copy these folders into the root of `local-agent-workshop/`.

The HTML template expects generated reports to be written to:

```text
reports/design-first/<run-id>.html
```

From there, links like `../../me.md` and `../../docs/...` resolve back to the repository root.
