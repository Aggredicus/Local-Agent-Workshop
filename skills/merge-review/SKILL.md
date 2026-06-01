# /merge-review

Use this skill before requesting approval, enabling auto-merge, merging a PR, or continuing a stacked PR sequence.

The goal is to make merge decisions explicit, evidence-linked, and human-governed.

## Core rule

```text
inspect before approval
approve only with evidence
merge only with human authorization
never bypass protected branch policy
```

## When to use

Use `/merge-review`:

- before merging any PR,
- before requesting human approval for a PR,
- after creating a stacked PR chain,
- after CI finishes,
- after a reviewer requests changes,
- before retargeting stacked PRs,
- when PRs may be stale, duplicated, blocked, or based on the wrong branch.

## Non-goals

This skill does not:

- merge PRs automatically,
- approve high-risk work on behalf of the human,
- change protected branch settings,
- bypass CI,
- bypass branch policy,
- treat dashboards as merge authority,
- treat generated projections as review evidence unless their source artifacts are also available.

## Inputs

Collect:

- repository name,
- target PR or PR stack,
- base branch for each PR,
- head branch for each PR,
- PR title/body,
- changed files,
- mergeability state,
- draft/open/closed/merged state,
- CI/workflow state when available,
- review submissions when available,
- requested reviewers when available,
- issue links,
- evidence paths,
- risk notes,
- known stack order.

## Inspection checklist

For each PR, inspect:

1. **State** — open, draft, closed, or merged.
2. **Base/head** — correct branch target and stacked base.
3. **Mergeability** — mergeable, conflicted, unknown, or blocked.
4. **Scope** — changed files match PR body and issue.
5. **Evidence** — tests, reports, docs, or examples are listed.
6. **CI** — required checks passed, pending, failed, missing, or unavailable.
7. **Review** — human approval, requested changes, missing review, or not required.
8. **Risk** — secrets, protected branches, public endpoints, infrastructure, Proxmox, destructive actions, or generated-authority confusion.
9. **Stack order** — dependency PRs must merge before dependent PRs.
10. **Stop conditions** — any uncertainty that requires handoff.

## Verdicts

Use one of these verdicts.

| Verdict | Meaning |
|---|---|
| `ready_for_human_approval` | PR appears reviewable, evidence is present, and only human approval remains. |
| `needs_ci` | CI or local verification is missing, pending, or failed. |
| `needs_review` | Human review or requested reviewer response is missing. |
| `blocked` | Dependency, conflict, failed check, requested changes, or missing evidence blocks merge. |
| `do_not_merge` | PR violates safety, authority, or branch policy boundaries. |
| `stack_wait` | PR may be good but must wait for an earlier PR in the stack. |

## Merge-order rules

For stacked PRs:

1. Merge root PRs first.
2. Merge independent PRs only after confirming they do not overlap risk boundaries.
3. Retarget dependent PRs after their base PR merges.
4. Re-check CI and mergeability after retargeting.
5. Do not merge a dependent PR while its base is unmerged unless the stack strategy explicitly requires it and a human approves.

## Human approval requirement

Human approval is required before:

- merging into protected branches,
- enabling auto-merge,
- publishing to stable branches,
- accepting high-risk governance changes,
- accepting security-sensitive changes,
- accepting Proxmox or local infrastructure changes,
- accepting destructive or externally visible behavior changes.

## Output format

Produce a merge-review packet:

```text
repo:
reviewed_at:
pr_stack:
recommended_order:

PR #:
  title:
  base:
  head:
  state:
  mergeable:
  ci_status:
  review_status:
  risk_level:
  changed_files:
  evidence:
  blockers:
  verdict:
  next_action:

summary:
  ready_for_human_approval:
  needs_ci:
  needs_review:
  blocked:
  do_not_merge:
  stack_wait:

human_decision_needed:
```

## Stop conditions

Stop and create a handoff if:

- PR state is unknown,
- mergeability is unknown and cannot be checked,
- CI status is missing for a code or validation change,
- required evidence is missing,
- branch base is wrong,
- PR stack order is unclear,
- requested changes are unresolved,
- the PR touches secrets, protected branch policy, public endpoints, infrastructure, Proxmox, or destructive behavior,
- the agent would need to approve its own high-risk work.

## Good merge-review behavior

A good `/merge-review` run should not merely say “looks good.” It should say:

- what was checked,
- what could not be checked,
- which PRs are ready,
- which PRs are waiting on stack order,
- which PRs need CI or review,
- which PRs are blocked,
- and what exact human decision is needed.
