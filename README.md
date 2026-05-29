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
repo -> task selection -> isolated branch/worktree -> work -> verify -> review card -> human decision -> resume
```

## Instruction hierarchy

All agent/tool adapter files point to `me.md`.

```text
AGENTS.md / CLAUDE.md / CODEX.md / Cursor rules
  ->
me.md
  ->
docs/, schemas/, skills/, workflows/, plan/, scripts/
  ->
runtime artifacts: chronicle/, reviews/, reports/, repo_graph/, .grind/
```

## Current status

Repository normalization and branch creation are complete enough to proceed. The canonical instruction spine, branch model, initial CI scaffold, and `/design-first` assets are installed.

The next focus is Issue #3: verify GitHub Actions CI with a smoke-test pull request into `develop`.

Temporary import zip files remain at the repository root by choice and can be moved to `archive/imports/` in a later cleanup.

## Next recommended steps

1. Verify GitHub Actions CI through a smoke-test pull request into `develop`.
2. Record the exact CI check name for branch protection.
3. Configure branch protection for `main` and `develop`.
4. Implement the first CLI command: `workshop init`.

## Key documents

- `me.md` — canonical instruction spine.
- `AGENTS.md`, `CLAUDE.md`, `CODEX.md` — thin pointer files for AI coding tools.
- `.branch-policy.yaml` — machine-readable branch governance.
- `docs/governance/BRANCH_POLICY.md` — human-readable branch policy.
- `docs/governance/RISK_POLICY.md` — risk and approval model.
- `docs/protocols/GRIND_PROTOCOL.md` — long-running autonomous work protocol.
- `docs/protocols/REVIEW_WORKFLOW.md` — review-card and human-decision workflow.
