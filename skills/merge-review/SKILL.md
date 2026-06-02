# /merge-review

Use this skill before requesting approval, enabling auto-merge, merging a PR, or continuing a stacked PR sequence.

The goal is to make merge decisions explicit, evidence-linked, and human-governed while allowing routine low-risk changes to proceed through a standing autonomous merge lane.

## Core rule

```text
inspect before approval
approve only with evidence
autonomous merge only inside the approved low-risk lane
explicit human approval required outside the low-risk lane
never bypass protected branch policy
prefer minimal merge payloads
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

- merge medium-risk or high-risk PRs without human approval,
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
7. **Review** — human approval, requested changes, missing review, or standing low-risk authorization.
8. **Risk** — secrets, protected branch settings, public endpoints, infrastructure, Proxmox, destructive actions, security-sensitive behavior, or generated-authority confusion.
9. **Stack order** — dependency PRs must merge before dependent PRs.
10. **Autonomous lane eligibility** — changed paths and risk profile must fit the low-risk lane before autonomous merge is allowed.
11. **Stop conditions** — any uncertainty that requires handoff.

## Verdicts

Use one of these verdicts.

| Verdict | Meaning |
|---|---|
| `ready_for_autonomous_merge` | PR passes review, fits the approved low-risk lane, and may be merged without another human confirmation. |
| `ready_for_human_approval` | PR appears reviewable, evidence is present, but explicit human approval is still required. |
| `needs_ci` | CI or local verification is missing, pending, or failed. |
| `needs_review` | Human review, requested reviewer response, or policy clarification is missing. |
| `blocked` | Dependency, conflict, failed check, requested changes, or missing evidence blocks merge. |
| `do_not_merge` | PR violates safety, authority, or branch policy boundaries. |
| `stack_wait` | PR may be good but must wait for an earlier PR in the stack. |

## Autonomous low-risk merge lane

`/merge-review` may produce `ready_for_autonomous_merge` only when every condition below is true:

- PR is open and non-draft.
- PR targets an allowed integration branch.
- PR is mergeable.
- CI is successful, or CI is not required and the reason is documented.
- Risk level is low.
- Diff is small and bounded.
- Changed files are limited to approved low-risk paths.
- PR body includes evidence and non-goals.
- No requested changes are unresolved.
- No protected branch settings are changed.
- No secrets, credentials, tokens, or environment files are touched.
- No Proxmox, host, deployment, public endpoint, infrastructure, payment, customer-data, destructive-command, migration, or security-sensitive behavior is touched.
- No generated projection is promoted to source of truth.
- Merge uses the minimal payload rule.

Approved low-risk paths:

```text
docs/**
skills/**/SKILL.md
examples/**
reports/review/**
reports/validation/**
```

Even inside approved paths, autonomous merge must stop if the content changes governance boundaries, approval boundaries, secrets, infrastructure, Proxmox behavior, security posture, protected branch settings, or source-of-truth status.

Human approval remains required for these paths unless a later reviewed policy explicitly relaxes them:

```text
.github/workflows/**
.github/ISSUE_TEMPLATE/**
.branch-policy.yaml
schemas/**
scripts/**
src/**
docs/governance/**
docs/security/**
docs/infrastructure/**
```

## Merge-order rules

For stacked PRs:

1. Merge root PRs first.
2. Merge independent PRs only after confirming they do not overlap risk boundaries.
3. Retarget dependent PRs after their base PR merges.
4. Re-check CI and mergeability after retargeting.
5. Do not merge a dependent PR while its base is unmerged unless the stack strategy explicitly requires it and the PR is either explicitly approved by a human or qualifies for the autonomous low-risk lane.

## Merge action payload guidance

When a PR is explicitly human-authorized or qualifies as `ready_for_autonomous_merge`, prefer the smallest normal merge action supported by the tool:

```text
repository_full_name
pr_number
```

Do not include custom merge metadata unless it is specifically required.

Avoid optional merge fields by default, including:

- custom commit title,
- custom commit message,
- expected head SHA,
- explicit merge method,
- long generated summaries.

Reason: long or highly customized merge payloads may hit tool-layer limits or safety checks even when the PR itself is safe and approved. The default GitHub merge behavior is usually the safest operational path after review.

If a merge attempt with optional fields is blocked by the tool layer, do not retry by adding more fields. Re-check authorization or autonomous-lane eligibility and use the minimal normal merge payload instead.

## Explicit human approval requirement

Explicit human approval is still required before:

- changing this autonomous merge policy,
- merging medium-risk or high-risk PRs,
- changing protected branch settings,
- enabling GitHub auto-merge globally,
- publishing to stable release branches,
- accepting high-risk governance changes,
- accepting security-sensitive changes,
- accepting Proxmox or local infrastructure changes,
- accepting destructive or externally visible behavior changes,
- accepting source-of-truth promotions,
- accepting migrations or persistent state changes.

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
  autonomous_lane_eligible:
  evidence:
  blockers:
  verdict:
  next_action:

summary:
  ready_for_autonomous_merge:
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
- the PR touches secrets, protected branch settings, public endpoints, infrastructure, Proxmox, security-sensitive behavior, or destructive behavior,
- autonomous-lane eligibility is uncertain,
- the PR would require the agent to approve its own medium-risk or high-risk work.

## Good merge-review behavior

A good `/merge-review` run should not merely say “looks good.” It should say:

- what was checked,
- what could not be checked,
- which PRs are ready for autonomous merge,
- which PRs are ready for human approval,
- which PRs are waiting on stack order,
- which PRs need CI or review,
- which PRs are blocked,
- and what exact human decision, if any, is needed.
