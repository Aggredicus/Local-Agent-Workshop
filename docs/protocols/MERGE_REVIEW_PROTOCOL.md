# Merge Review Protocol

The merge review protocol defines how Local Agent Workshop evaluates PRs and PR stacks before approval or merge.

It complements branch policy, human approval boundaries, review workflow, cleanup protocol, publish protocol, and `skills/merge-review/SKILL.md`.

## Principle

Merging is a protected decision point.

Agents may inspect, summarize, recommend, prepare evidence, and merge PRs only when they fall entirely inside the approved autonomous low-risk lane.

Explicit human approval remains required outside that low-risk lane.

When merge is authorized by either explicit human approval or the autonomous low-risk lane, prefer the smallest normal merge action supported by the tool.

Governance-relevant docs are operational authority, not ordinary docs. If they change canonical instructions, approval boundaries, merge behavior, source-of-truth status, or global skill rules, the merge-review packet must record authorization context.

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
| `ready_for_autonomous_merge` | Evidence and checks are sufficient, the PR fits the approved low-risk lane, authorization context exists if needed, and no additional human confirmation is required. |
| `ready_for_human_approval` | Evidence and checks are sufficient, but explicit human approval is still required. |
| `needs_authorization_note` | PR changes governance-relevant docs but lacks explicit authorization context in the PR body, issue, review packet, or task instruction. |
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
11. Whether canonical instructions, global skill rules, merge policy, approval boundaries, source-of-truth status, or governance behavior changed.
12. Authorization context for governance-relevant docs changes.
13. Stack order and dependency PRs.
14. Autonomous-lane eligibility.

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
- No protected branch or approval-boundary settings are changed.
- No sensitive configuration, live runtime behavior, infrastructure effect, external endpoint exposure, migration, or source-of-truth promotion is touched.
- Governance-relevant docs are either unchanged or include explicit authorization context.
- Merge uses the minimal payload rule.

Approved low-risk paths:

```text
docs/**
skills/**/SKILL.md
examples/**
reports/review/**
reports/validation/**
```

Even inside these paths, autonomous merge must stop if the content changes governance boundaries, approval boundaries, sensitive configuration, infrastructure posture, security posture, protected branch settings, or source-of-truth status without authorization context.

## Governance-relevant docs rule

Some docs are operational authority, not merely explanatory text. Changes to these files may be docs-only but still governance-relevant:

```text
me.md
AGENTS.md
skills/README.md
skills/merge-review/SKILL.md
skills/close-issue/SKILL.md
docs/governance/**
docs/protocols/MERGE_REVIEW_PROTOCOL.md
docs/protocols/STANDARD_EXECUTION_CONTRACT.md
docs/protocols/REPO_VALIDATION_GATE.md
.branch-policy.yaml
.github/ISSUE_TEMPLATE/**
```

A governance-relevant docs PR may still be merged after review, but merge review must not classify it as ordinary docs-only work. It must record:

```text
governance_relevant: yes
changed_authority_surface: <what changed>
authorization_context: <issue, PR comment, or explicit human instruction>
autonomous_lane_eligible: yes | no
```

If authorization context is missing, use `needs_authorization_note` or `ready_for_human_approval`, not `ready_for_autonomous_merge`.

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
- governance-relevant docs changed without authorization context,
- protected branch or approval-boundary settings changed without explicit human approval,
- sensitive configuration or externally visible behavior is touched without explicit human approval,
- generated projections are treated as source of truth,
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
- changing protected branch or approval-boundary settings,
- enabling global auto-merge behavior,
- publishing to stable release branches,
- accepting high-risk governance changes,
- accepting security-sensitive changes,
- accepting infrastructure or runtime behavior changes,
- accepting externally visible behavior changes,
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
- governance relevance,
- changed authority surface,
- authorization context,
- autonomous-lane eligibility,
- evidence paths,
- risk notes,
- verdict,
- next action,
- human decision needed.

## Current stack example

For the current post-preparation sprint, low-risk documentation cleanup PRs may qualify for `ready_for_autonomous_merge` after this policy is merged.

Runtime, schema, script, workflow, infrastructure, security, or governance changes should continue to use `ready_for_human_approval` unless a later policy deliberately grants a narrower autonomous lane.

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

This protocol does not enable global auto-merge, weaken branch protection, approve high-risk changes, or authorize infrastructure/deployment changes without human approval.
