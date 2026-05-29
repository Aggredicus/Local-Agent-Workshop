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
