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
11. Quality must be analyzed at the beginning of meaningful work and again after closeout before human review.
12. Publishing to `main` must be quality-gated, evidence-linked, and explicitly human-approved.

## Canonical automation loop

Every meaningful automation cycle should follow this order unless explicitly skipped with a reason:

```text
/cleanup preflight
→ /quality-analysis baseline
→ /generate-issue start-check
→ /grind
→ /self-improvement
→ /generate-issue closeout-check
→ /cleanup closeout
→ /quality-analysis final review gate
→ review/human decision
```

### Loop intent

- `/cleanup preflight` confirms the repository is synchronized, tidy, and safe to work in.
- `/quality-analysis baseline` checks whether the intended work is clear, scoped, testable, and worth doing.
- `/generate-issue start-check` confirms there is a valid issue/card or creates/simplifies/skips one through reviewable logic.
- `/grind` performs bounded implementation, documentation, testing, or review-preparation work.
- `/self-improvement` reflects from evidence and writes bounded JSON proposals or lessons without silently mutating governance.
- `/generate-issue closeout-check` creates or skips follow-up issue candidates after duplicate/value checks.
- `/cleanup closeout` leaves the repository synchronized, reviewable, and free of unresolved cleanup blockers.
- `/quality-analysis final review gate` evaluates the complete closeout package before human review.
- `review/human decision` approves, modifies, rejects, merges, defers, redirects, or authorizes `/publish`.

The loop should remain cost-aware:

```text
Analyze only enough.
Create only bounded follow-up work.
Stop when value drops below cost.
Escalate only at risk boundaries.
```

## Cleanup protocol

Read:

- `docs/protocols/REPOSITORY_CLEANUP_PROTOCOL.md`
- `skills/repo-cleanup/SKILL.md`

Every meaningful work session has two cleanup gates:

```text
Preflight cleanup gate  = before changing files
Closeout cleanup gate   = before final quality analysis and human review
```

Suggested commands:

```sh
python scripts/repo_cleanup.py --phase before
# perform scoped work
python scripts/repo_cleanup.py --phase after
```

Cleanup is non-destructive by default. Agents may propose cleanup actions, but must not silently delete branches, remove audit/history files, close high-risk review cards, alter protected branches, rewrite Chronicle events, or bypass human approval gates.

## Quality analysis protocol

Read:

- `docs/protocols/QUALITY_ANALYSIS_PROTOCOL.md`
- `skills/quality-analysis/SKILL.md`

Quality analysis has two gates:

```text
Baseline quality analysis      = after cleanup preflight, before issue/start work decisions
Final review quality analysis  = after cleanup closeout, before review/human decision
```

Baseline quality analysis asks:

- Is the intended work clear?
- Is the scope bounded?
- Are acceptance criteria present?
- Are expected tests/docs known?
- Is the risk level understood?
- Should work proceed, split, simplify, or escalate?

Final review quality analysis asks:

- Did the work meet acceptance criteria?
- Is evidence real and specific?
- Did cleanup closeout pass?
- Are follow-up issue decisions complete?
- Are risks and limitations documented?
- Is the package ready for human review?
- Is the package ready for `/publish`, if publishing is requested?

## Publish protocol

Read:

- `docs/protocols/PUBLISH_PROTOCOL.md`
- `skills/publish/SKILL.md`

Use `/publish` only after review/human decision explicitly approves promoting reviewed `develop` work into `main`.

Branch meaning:

```text
main     stable, released, client-safe code
develop  reviewed integration branch
```

`/publish` is quality-gated. It depends on a successful `/quality-analysis final review gate` pass and a configurable publish approval profile.

Agents may prepare publish packets, incident summaries, quality summaries, changelog summaries, `develop` → `main` PRs, and readiness recommendations.

Agents must not silently merge into `main`, bypass branch protection, ignore failed verification, hide incidents, erase audit history, or publish without explicit human approval.

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
