# Merge Review Protocol

The merge review protocol defines how Local Agent Workshop evaluates PRs and PR stacks before approval or merge.

It complements the branch policy, human approval boundaries, review workflow, cleanup protocol, and publish protocol.

## Principle

Merging is a protected decision point.

Agents may inspect, summarize, recommend, prepare evidence, and merge PRs that fall entirely inside the approved autonomous low-risk lane.

Explicit human approval remains required outside that low-risk lane.

When merge is authorized by either explicit human approval or the autonomous low-risk lane, prefer the smallest normal merge action supported by the tool.

## Relationship to other policies

Read alongside:

- `me.md`
- `docs/governance/BRANCH_POLICY.md`
- `docs/governance/HUMAN_APPROVAL_BOUNDARIES.md`
- `docs/governance/RISK_POLICY.md`
- `docs/protocols/REVIEW_WORKFLOW.md`
- `docs/protocols/PUBLISH_PROTOCOL.md`
- `skills/merge-review/SKILL.md`

## Review states

| State | Meaning |
|---|---|
| `ready_for_autonomous_merge` | Evidence and checks are sufficient, the PR fits the approved low-risk lane, and no additional human confirmation is required. |
| `ready_for_human_approval` | Evidence and checks are sufficient, but explicit human approval is still required. |
| `needs_ci` | CI or verification is missing, failed, or pending. |
| `needs_review` | Human review, requested reviewer response, or policy clarification is missing. |
| `blocked` | Dependency, stack order, conflict, requested changes, or evidence problem blocks merge. |
| `do_not_merge` | Safety, authority, or branch policy boundary is violated. |
| `stack_wait` | PR is acceptable only after an earlier stacked PR merges and the branch is retargeted/rechecked. |

## Required checks

A merge-review should inspect:

1. PR title and body.
2. Linked issue or reason for no linked issue.
3. Base and head branches.
4. Draft/open/closed/merged state.
5. Mergeability.
6. Changed files.
7. CI or workflow runs when available.
8. Review submissions and requested reviewers when available.
9. Evidence paths and skipped checks.
10. Risk notes and non-goals.
11. Stack order and dependency PRs.
12. Autonomous-lane eligibility.

## Autonomous low-risk merge lane

A PR may be merged without additional human confirmation only when every condition below is true:

- PR is open and non-draft.
- PR targets an allowed integration branch.
- PR is mergeable.
- CI is successful, or CI is not required and the reason is documented.
- `/merge-review` verdict is `ready_for_autonomous_merge`.
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

Even inside these paths, autonomous merge must stop if the content changes governance boundaries, approval boundaries, secrets, infrastructure, Proxmox behavior, security posture, protected branch settings, or source-of-truth status.

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

## Stacked PR protocol

For a stack such as:

```text
PR A → PR B → PR C
```

Use this process:

1. Review PR A against its base branch.
2. Review PR B against PR A's branch.
3. Review PR C against PR B's branch.
4. Mark PR B and PR C as `stack_wait` until their bases merge.
5. After PR A merges, retarget PR B to the new integration branch.
6. Re-check CI, mergeability, and diff shape.
7. Repeat for the rest of the stack.

## Merge gates

Do not recommend merge if:

- the PR is draft,
- mergeability is false or unknown and cannot be resolved,
- required CI failed or is missing for code/validation changes,
- human review is required and absent,
- requested changes are unresolved,
- the PR changes protected branch policy without explicit human approval,
- the PR includes secrets or private credentials,
- the PR exposes local endpoints publicly,
- the PR performs Proxmox or host mutation without explicit approval,
- the PR changes generated projections as if they were source of truth,
- the PR lacks evidence for its acceptance criteria,
- autonomous-lane eligibility is uncertain.

## Merge action payload

After merge is authorized by explicit human approval or by the autonomous low-risk lane, prefer the minimal normal merge payload:

```text
repository_full_name
pr_number
```

Avoid optional merge fields unless specifically required:

- custom commit title,
- custom commit message,
- expected head SHA,
- explicit merge method,
- long generated summaries.

Long or highly customized merge payloads may hit tool-layer limits or safety checks even when the PR itself is safe and approved. If an optional-field merge attempt is blocked by the tool layer, re-check authorization or autonomous-lane eligibility and retry only with the minimal normal merge payload.

## Explicit human approval requirements

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

## Evidence expectations

Every merge-review packet should include:

- what was checked,
- what could not be checked,
- current PR state,
- mergeability,
- CI status,
- review status,
- changed files,
- autonomous-lane eligibility,
- evidence paths,
- risk notes,
- verdict,
- next action,
- human decision needed.

## Current stack example

For the current post-preparation sprint, low-risk documentation cleanup PRs may qualify for `ready_for_autonomous_merge` after this policy is merged.

Runtime, schema, script, workflow, infrastructure, Proxmox, security, or governance changes should continue to use `ready_for_human_approval` unless a later policy deliberately grants a narrower autonomous lane.

## Output example

```text
repo: Aggredicus/Local-Agent-Workshop
reviewed_at: 2026-06-01
recommended_order: #129

PR #129:
  verdict: ready_for_autonomous_merge
  next_action: merge with minimal payload

human_decision_needed:
  none
```

## Non-goals

This protocol does not enable GitHub auto-merge globally, weaken branch protection, approve high-risk changes, or authorize infrastructure/deployment changes without human approval.
