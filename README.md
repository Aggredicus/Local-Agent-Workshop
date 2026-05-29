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
repo → cleanup preflight → task selection → isolated branch/worktree → work → verify → cleanup closeout → review card → human decision → resume
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
runtime artifacts: chronicle/, reviews/, reports/, repo_graph/, .grind/, orchestration/
```

## Current status

Repository normalization and branch creation are complete enough to proceed with iterative implementation on `develop`.

The repository now includes:

- the canonical instruction spine in `me.md`,
- branch governance documents,
- risk and human-approval policies,
- HyperKanban state, packet, validator, and CLI commands,
- evidence-gated HyperKanban completion,
- repository cleanup protocol and `/repo-cleanup` skill,
- a non-destructive cleanup audit script.

## Next recommended steps

1. Finish cleanup automation and enforcement from #37.
2. Implement high-concurrency multi-agent orchestration from #35.
3. Add cleanup evidence fields to PR/review templates.
4. Add card leases, stack plans, merge trains, and context packs.
5. Continue hardening CI, verification, and branch protection.

## Key documents

- `me.md` — canonical instruction spine.
- `AGENTS.md`, `CLAUDE.md`, `CODEX.md` — thin pointer files for AI coding tools.
- `.branch-policy.yaml` — machine-readable branch governance.
- `docs/governance/BRANCH_POLICY.md` — human-readable branch policy.
- `docs/governance/RISK_POLICY.md` — risk and approval model.
- `docs/protocols/GRIND_PROTOCOL.md` — long-running autonomous work protocol.
- `docs/protocols/REPOSITORY_CLEANUP_PROTOCOL.md` — cleanup preflight and closeout protocol.
- `docs/protocols/REVIEW_WORKFLOW.md` — review-card and human-decision workflow.
- `orchestration/hyperkanban/README.md` — HyperKanban state and packet contract.
