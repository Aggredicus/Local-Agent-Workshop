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

This repository is completing Issue #1: repository normalization from uploaded starter assets into a working Local Agent Workshop project root.

## First recommended steps

1. Finish repository normalization from uploaded zip assets.
2. Confirm `me.md` as the canonical instruction spine.
3. Create `develop` and `experimental` branches.
4. Verify GitHub Actions CI.
5. Implement the first CLI command: `workshop init`.

## Key documents

- `me.md` — canonical instruction spine.
- `AGENTS.md`, `CLAUDE.md`, `CODEX.md` — thin pointer files for AI coding tools.
- `.branch-policy.yaml` — machine-readable branch governance.
- `docs/governance/BRANCH_POLICY.md` — human-readable branch policy.
- `docs/governance/RISK_POLICY.md` — risk and approval model.
- `docs/protocols/GRIND_PROTOCOL.md` — long-running autonomous work protocol.
- `docs/protocols/REVIEW_WORKFLOW.md` — review-card and human-decision workflow.
