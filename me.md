# me.md — Canonical Instruction Spine

This file is the canonical instruction spine for Local Agent Workshop.

All agent/tool adapter files such as `AGENTS.md`, `CLAUDE.md`, `CODEX.md`, and Cursor rules must point here instead of duplicating the full policy.

## Product identity

- Product name: **Local Agent Workshop**
- Repository name: `local-agent-workshop`
- CLI command: `workshop`

## Mission

Build a local-first, human-governed autonomous development workshop where LLM agents can run long-duration coding, testing, documentation, repo graph, and review preparation work while preserving human control at risk boundaries.

## Golden rule

Tool adapter files point to this file. This file routes agents to the rest of the repository.

```text
AGENTS.md / CLAUDE.md / CODEX.md / Cursor rules
  ↓
me.md
  ↓
docs/, schemas/, skills/, workflows/, plan/, scripts/
  ↓
chronicle/, reviews/, reports/, repo_graph/, .grind/
```

## Operating principles

1. Work locally first whenever practical.
2. Use branch-aware automation.
3. Never merge into protected branches without explicit human approval.
4. Produce reviewable patches, not silent production mutations.
5. Long-running grind is allowed, but it must be checkpointed and resumable.
6. Sensitive work is allowed in safe forms, but live effects require approval.
7. Every meaningful action should leave a Chronicle event.
8. Agents should stay quiet unless human judgment is truly required.
9. The workshop may improve itself only through reviewable proposals.
10. Clean before work and clean after work using the repository cleanup protocol.

## Cleanup protocol

Read:

- `docs/protocols/REPOSITORY_CLEANUP_PROTOCOL.md`
- `skills/repo-cleanup/SKILL.md`

Every meaningful work session has two cleanup gates:

```text
Preflight cleanup gate  = before changing files
Closeout cleanup gate   = before opening/merging/ending work
```

Suggested commands:

```sh
python scripts/repo_cleanup.py --phase before
# perform scoped work
python scripts/repo_cleanup.py --phase after
```

Cleanup is non-destructive by default. Agents may propose cleanup actions, but must not silently delete branches, remove audit/history files, close high-risk review cards, alter protected branches, rewrite Chronicle events, or bypass human approval gates.

## Branch model

Read:

- `docs/governance/BRANCH_POLICY.md`
- `.branch-policy.yaml`

Default branches:

```text
main          stable/client-safe/released code
develop       reviewed integration
experimental  sandbox and lab work
agent/*       autonomous work branches
release/*     release candidates
```

## Risk boundaries

Read:

- `docs/governance/RISK_POLICY.md`
- `docs/governance/HUMAN_APPROVAL_BOUNDARIES.md`
- `docs/governance/AUTONOMOUS_AGENT_POLICY.md`

Agents may analyze, draft, test, simulate, refactor, and prepare reviewable patches for sensitive areas. Agents must pause before activating sensitive consequences such as live credentials, production payment changes, destructive actions, or protected branch merges.

## Grind protocol

Read:

- `docs/protocols/GRIND_PROTOCOL.md`
- `docs/protocols/CHECKPOINT_RESUME_PROTOCOL.md`
- `docs/protocols/REVIEW_WORKFLOW.md`

Every grind run must have:

- run ID,
- branch/worktree,
- current task,
- checkpoint state,
- verification evidence,
- review card,
- and resume command.

## Review workflow

Review artifacts live in:

```text
reviews/pending/
reviews/approved/
reviews/rejected/
reviews/modified/
reports/morning-review.md
```

Every patch should answer:

- What changed?
- Why?
- What passed?
- What failed?
- What risks remain?
- What decision is needed?
- What happens next?

## Chronicle events

Meaningful actions should write immutable JSON events under:

```text
chronicle/events/
```

## Verification

Use these scripts when available:

```text
scripts/ci-local.sh
scripts/verify.sh
scripts/test-fast.sh
scripts/test-full.sh
scripts/security-scan.sh
scripts/release-check.sh
```
