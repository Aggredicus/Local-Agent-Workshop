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
# Local Agent Workshop

**Local Agent Workshop** is a local-first, human-governed autonomous software development workspace for long-running LLM-assisted coding, reviewable patches, branch-aware automation, Chronicle event logs, repo graphs, and clear human approval at risk boundaries.

Working repository name:

```text
local-agent-workshop
```

CLI command name:

```text
workshop
```

## Core loop

```text
repo → task selection → isolated branch/worktree → work → verify → review card → human decision → resume
```

## Instruction hierarchy

All agent/tool adapter files point to `me.md`.

```text
AGENTS.md / CLAUDE.md / CODEX.md / Cursor rules
  ↓
me.md
  ↓
docs/, schemas/, skills/, workflows/, plan/, scripts/
  ↓
runtime artifacts: chronicle/, reviews/, reports/, repo_graph/, .grind/
```

## Current status

The repository is being normalized from uploaded starter zip assets. See Issue #1 for the current bootstrap task.

## First recommended steps

1. Finish repository normalization from uploaded zip assets.
2. Confirm `me.md` as the canonical instruction spine.
3. Create `develop` and `experimental` branches.
4. Verify GitHub Actions CI.
5. Implement the first CLI command: `workshop init`.
